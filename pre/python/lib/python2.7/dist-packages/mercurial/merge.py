# merge.py - directory-level update/merge handling for Mercurial
#
# Copyright 2006, 2007 Matt Mackall <mpm@selenic.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

import errno
import shutil
import stat
import struct

from .i18n import _
from .node import (
    addednodeid,
    bin,
    hex,
    modifiednodeid,
    nullhex,
    nullid,
    nullrev,
)
from .pycompat import delattr
from .thirdparty import attr
from . import (
    copies,
    encoding,
    error,
    filemerge,
    match as matchmod,
    obsutil,
    pathutil,
    pycompat,
    scmutil,
    subrepoutil,
    util,
    worker,
)
from .utils import hashutil

_pack = struct.pack
_unpack = struct.unpack


def _droponode(data):
    # used for compatibility for v1
    bits = data.split(b'\0')
    bits = bits[:-2] + bits[-1:]
    return b'\0'.join(bits)


# Merge state record types. See ``mergestate`` docs for more.
RECORD_LOCAL = b'L'
RECORD_OTHER = b'O'
RECORD_MERGED = b'F'
RECORD_CHANGEDELETE_CONFLICT = b'C'
RECORD_MERGE_DRIVER_MERGE = b'D'
RECORD_PATH_CONFLICT = b'P'
RECORD_MERGE_DRIVER_STATE = b'm'
RECORD_FILE_VALUES = b'f'
RECORD_LABELS = b'l'
RECORD_OVERRIDE = b't'
RECORD_UNSUPPORTED_MANDATORY = b'X'
RECORD_UNSUPPORTED_ADVISORY = b'x'

MERGE_DRIVER_STATE_UNMARKED = b'u'
MERGE_DRIVER_STATE_MARKED = b'm'
MERGE_DRIVER_STATE_SUCCESS = b's'

MERGE_RECORD_UNRESOLVED = b'u'
MERGE_RECORD_RESOLVED = b'r'
MERGE_RECORD_UNRESOLVED_PATH = b'pu'
MERGE_RECORD_RESOLVED_PATH = b'pr'
MERGE_RECORD_DRIVER_RESOLVED = b'd'

ACTION_FORGET = b'f'
ACTION_REMOVE = b'r'
ACTION_ADD = b'a'
ACTION_GET = b'g'
ACTION_PATH_CONFLICT = b'p'
ACTION_PATH_CONFLICT_RESOLVE = b'pr'
ACTION_ADD_MODIFIED = b'am'
ACTION_CREATED = b'c'
ACTION_DELETED_CHANGED = b'dc'
ACTION_CHANGED_DELETED = b'cd'
ACTION_MERGE = b'm'
ACTION_LOCAL_DIR_RENAME_GET = b'dg'
ACTION_DIR_RENAME_MOVE_LOCAL = b'dm'
ACTION_KEEP = b'k'
ACTION_EXEC = b'e'
ACTION_CREATED_MERGE = b'cm'


class mergestate(object):
    '''track 3-way merge state of individual files

    The merge state is stored on disk when needed. Two files are used: one with
    an old format (version 1), and one with a new format (version 2). Version 2
    stores a superset of the data in version 1, including new kinds of records
    in the future. For more about the new format, see the documentation for
    `_readrecordsv2`.

    Each record can contain arbitrary content, and has an associated type. This
    `type` should be a letter. If `type` is uppercase, the record is mandatory:
    versions of Mercurial that don't support it should abort. If `type` is
    lowercase, the record can be safely ignored.

    Currently known records:

    L: the node of the "local" part of the merge (hexified version)
    O: the node of the "other" part of the merge (hexified version)
    F: a file to be merged entry
    C: a change/delete or delete/change conflict
    D: a file that the external merge driver will merge internally
       (experimental)
    P: a path conflict (file vs directory)
    m: the external merge driver defined for this merge plus its run state
       (experimental)
    f: a (filename, dictionary) tuple of optional values for a given file
    X: unsupported mandatory record type (used in tests)
    x: unsupported advisory record type (used in tests)
    l: the labels for the parts of the merge.

    Merge driver run states (experimental):
    u: driver-resolved files unmarked -- needs to be run next time we're about
       to resolve or commit
    m: driver-resolved files marked -- only needs to be run before commit
    s: success/skipped -- does not need to be run any more

    Merge record states (stored in self._state, indexed by filename):
    u: unresolved conflict
    r: resolved conflict
    pu: unresolved path conflict (file conflicts with directory)
    pr: resolved path conflict
    d: driver-resolved conflict

    The resolve command transitions between 'u' and 'r' for conflicts and
    'pu' and 'pr' for path conflicts.
    '''

    statepathv1 = b'merge/state'
    statepathv2 = b'merge/state2'

    @staticmethod
    def clean(repo, node=None, other=None, labels=None):
        """Initialize a brand new merge state, removing any existing state on
        disk."""
        ms = mergestate(repo)
        ms.reset(node, other, labels)
        return ms

    @staticmethod
    def read(repo):
        """Initialize the merge state, reading it from disk."""
        ms = mergestate(repo)
        ms._read()
        return ms

    def __init__(self, repo):
        """Initialize the merge state.

        Do not use this directly! Instead call read() or clean()."""
        self._repo = repo
        self._dirty = False
        self._labels = None

    def reset(self, node=None, other=None, labels=None):
        self._state = {}
        self._stateextras = {}
        self._local = None
        self._other = None
        self._labels = labels
        for var in ('localctx', 'otherctx'):
            if var in vars(self):
                delattr(self, var)
        if node:
            self._local = node
            self._other = other
        self._readmergedriver = None
        if self.mergedriver:
            self._mdstate = MERGE_DRIVER_STATE_SUCCESS
        else:
            self._mdstate = MERGE_DRIVER_STATE_UNMARKED
        shutil.rmtree(self._repo.vfs.join(b'merge'), True)
        self._results = {}
        self._dirty = False

    def _read(self):
        """Analyse each record content to restore a serialized state from disk

        This function process "record" entry produced by the de-serialization
        of on disk file.
        """
        self._state = {}
        self._stateextras = {}
        self._local = None
        self._other = None
        for var in ('localctx', 'otherctx'):
            if var in vars(self):
                delattr(self, var)
        self._readmergedriver = None
        self._mdstate = MERGE_DRIVER_STATE_SUCCESS
        unsupported = set()
        records = self._readrecords()
        for rtype, record in records:
            if rtype == RECORD_LOCAL:
                self._local = bin(record)
            elif rtype == RECORD_OTHER:
                self._other = bin(record)
            elif rtype == RECORD_MERGE_DRIVER_STATE:
                bits = record.split(b'\0', 1)
                mdstate = bits[1]
                if len(mdstate) != 1 or mdstate not in (
                    MERGE_DRIVER_STATE_UNMARKED,
                    MERGE_DRIVER_STATE_MARKED,
                    MERGE_DRIVER_STATE_SUCCESS,
                ):
                    # the merge driver should be idempotent, so just rerun it
                    mdstate = MERGE_DRIVER_STATE_UNMARKED

                self._readmergedriver = bits[0]
                self._mdstate = mdstate
            elif rtype in (
                RECORD_MERGED,
                RECORD_CHANGEDELETE_CONFLICT,
                RECORD_PATH_CONFLICT,
                RECORD_MERGE_DRIVER_MERGE,
            ):
                bits = record.split(b'\0')
                self._state[bits[0]] = bits[1:]
            elif rtype == RECORD_FILE_VALUES:
                filename, rawextras = record.split(b'\0', 1)
                extraparts = rawextras.split(b'\0')
                extras = {}
                i = 0
                while i < len(extraparts):
                    extras[extraparts[i]] = extraparts[i + 1]
                    i += 2

                self._stateextras[filename] = extras
            elif rtype == RECORD_LABELS:
                labels = record.split(b'\0', 2)
                self._labels = [l for l in labels if len(l) > 0]
            elif not rtype.islower():
                unsupported.add(rtype)
        self._results = {}
        self._dirty = False

        if unsupported:
            raise error.UnsupportedMergeRecords(unsupported)

    def _readrecords(self):
        """Read merge state from disk and return a list of record (TYPE, data)

        We read data from both v1 and v2 files and decide which one to use.

        V1 has been used by version prior to 2.9.1 and contains less data than
        v2. We read both versions and check if no data in v2 contradicts
        v1. If there is not contradiction we can safely assume that both v1
        and v2 were written at the same time and use the extract data in v2. If
        there is contradiction we ignore v2 content as we assume an old version
        of Mercurial has overwritten the mergestate file and left an old v2
        file around.

        returns list of record [(TYPE, data), ...]"""
        v1records = self._readrecordsv1()
        v2records = self._readrecordsv2()
        if self._v1v2match(v1records, v2records):
            return v2records
        else:
            # v1 file is newer than v2 file, use it
            # we have to infer the "other" changeset of the merge
            # we cannot do better than that with v1 of the format
            mctx = self._repo[None].parents()[-1]
            v1records.append((RECORD_OTHER, mctx.hex()))
            # add place holder "other" file node information
            # nobody is using it yet so we do no need to fetch the data
            # if mctx was wrong `mctx[bits[-2]]` may fails.
            for idx, r in enumerate(v1records):
                if r[0] == RECORD_MERGED:
                    bits = r[1].split(b'\0')
                    bits.insert(-2, b'')
                    v1records[idx] = (r[0], b'\0'.join(bits))
            return v1records

    def _v1v2match(self, v1records, v2records):
        oldv2 = set()  # old format version of v2 record
        for rec in v2records:
            if rec[0] == RECORD_LOCAL:
                oldv2.add(rec)
            elif rec[0] == RECORD_MERGED:
                # drop the onode data (not contained in v1)
                oldv2.add((RECORD_MERGED, _droponode(rec[1])))
        for rec in v1records:
            if rec not in oldv2:
                return False
        else:
            return True

    def _readrecordsv1(self):
        """read on disk merge state for version 1 file

        returns list of record [(TYPE, data), ...]

        Note: the "F" data from this file are one entry short
              (no "other file node" entry)
        """
        records = []
        try:
            f = self._repo.vfs(self.statepathv1)
            for i, l in enumerate(f):
                if i == 0:
                    records.append((RECORD_LOCAL, l[:-1]))
                else:
                    records.append((RECORD_MERGED, l[:-1]))
            f.close()
        except IOError as err:
            if err.errno != errno.ENOENT:
                raise
        return records

    def _readrecordsv2(self):
        """read on disk merge state for version 2 file

        This format is a list of arbitrary records of the form:

          [type][length][content]

        `type` is a single character, `length` is a 4 byte integer, and
        `content` is an arbitrary byte sequence of length `length`.

        Mercurial versions prior to 3.7 have a bug where if there are
        unsupported mandatory merge records, attempting to clear out the merge
        state with hg update --clean or similar aborts. The 't' record type
        works around that by writing out what those versions treat as an
        advisory record, but later versions interpret as special: the first
        character is the 'real' record type and everything onwards is the data.

        Returns list of records [(TYPE, data), ...]."""
        records = []
        try:
            f = self._repo.vfs(self.statepathv2)
            data = f.read()
            off = 0
            end = len(data)
            while off < end:
                rtype = data[off : off + 1]
                off += 1
                length = _unpack(b'>I', data[off : (off + 4)])[0]
                off += 4
                record = data[off : (off + length)]
                off += length
                if rtype == RECORD_OVERRIDE:
                    rtype, record = record[0:1], record[1:]
                records.append((rtype, record))
            f.close()
        except IOError as err:
            if err.errno != errno.ENOENT:
                raise
        return records

    @util.propertycache
    def mergedriver(self):
        # protect against the following:
        # - A configures a malicious merge driver in their hgrc, then
        #   pauses the merge
        # - A edits their hgrc to remove references to the merge driver
        # - A gives a copy of their entire repo, including .hg, to B
        # - B inspects .hgrc and finds it to be clean
        # - B then continues the merge and the malicious merge driver
        #  gets invoked
        configmergedriver = self._repo.ui.config(
            b'experimental', b'mergedriver'
        )
        if (
            self._readmergedriver is not None
            and self._readmergedriver != configmergedriver
        ):
            raise error.ConfigError(
                _(b"merge driver changed since merge started"),
                hint=_(b"revert merge driver change or abort merge"),
            )

        return configmergedriver

    @util.propertycache
    def localctx(self):
        if self._local is None:
            msg = b"localctx accessed but self._local isn't set"
            raise error.ProgrammingError(msg)
        return self._repo[self._local]

    @util.propertycache
    def otherctx(self):
        if self._other is None:
            msg = b"otherctx accessed but self._other isn't set"
            raise error.ProgrammingError(msg)
        return self._repo[self._other]

    def active(self):
        """Whether mergestate is active.

        Returns True if there appears to be mergestate. This is a rough proxy
        for "is a merge in progress."
        """
        # Check local variables before looking at filesystem for performance
        # reasons.
        return (
            bool(self._local)
            or bool(self._state)
            or self._repo.vfs.exists(self.statepathv1)
            or self._repo.vfs.exists(self.statepathv2)
        )

    def commit(self):
        """Write current state on disk (if necessary)"""
        if self._dirty:
            records = self._makerecords()
            self._writerecords(records)
            self._dirty = False

    def _makerecords(self):
        records = []
        records.append((RECORD_LOCAL, hex(self._local)))
        records.append((RECORD_OTHER, hex(self._other)))
        if self.mergedriver:
            records.append(
                (
                    RECORD_MERGE_DRIVER_STATE,
                    b'\0'.join([self.mergedriver, self._mdstate]),
                )
            )
        # Write out state items. In all cases, the value of the state map entry
        # is written as the contents of the record. The record type depends on
        # the type of state that is stored, and capital-letter records are used
        # to prevent older versions of Mercurial that do not support the feature
        # from loading them.
        for filename, v in pycompat.iteritems(self._state):
            if v[0] == MERGE_RECORD_DRIVER_RESOLVED:
                # Driver-resolved merge. These are stored in 'D' records.
                records.append(
                    (RECORD_MERGE_DRIVER_MERGE, b'\0'.join([filename] + v))
                )
            elif v[0] in (
                MERGE_RECORD_UNRESOLVED_PATH,
                MERGE_RECORD_RESOLVED_PATH,
            ):
                # Path conflicts. These are stored in 'P' records.  The current
                # resolution state ('pu' or 'pr') is stored within the record.
                records.append(
                    (RECORD_PATH_CONFLICT, b'\0'.join([filename] + v))
                )
            elif v[1] == nullhex or v[6] == nullhex:
                # Change/Delete or Delete/Change conflicts. These are stored in
                # 'C' records. v[1] is the local file, and is nullhex when the
                # file is deleted locally ('dc'). v[6] is the remote file, and
                # is nullhex when the file is deleted remotely ('cd').
                records.append(
                    (RECORD_CHANGEDELETE_CONFLICT, b'\0'.join([filename] + v))
                )
            else:
                # Normal files.  These are stored in 'F' records.
                records.append((RECORD_MERGED, b'\0'.join([filename] + v)))
        for filename, extras in sorted(pycompat.iteritems(self._stateextras)):
            rawextras = b'\0'.join(
                b'%s\0%s' % (k, v) for k, v in pycompat.iteritems(extras)
            )
            records.append(
                (RECORD_FILE_VALUES, b'%s\0%s' % (filename, rawextras))
            )
        if self._labels is not None:
            labels = b'\0'.join(self._labels)
            records.append((RECORD_LABELS, labels))
        return records

    def _writerecords(self, records):
        """Write current state on disk (both v1 and v2)"""
        self._writerecordsv1(records)
        self._writerecordsv2(records)

    def _writerecordsv1(self, records):
        """Write current state on disk in a version 1 file"""
        f = self._repo.vfs(self.statepathv1, b'wb')
        irecords = iter(records)
        lrecords = next(irecords)
        assert lrecords[0] == RECORD_LOCAL
        f.write(hex(self._local) + b'\n')
        for rtype, data in irecords:
            if rtype == RECORD_MERGED:
                f.write(b'%s\n' % _droponode(data))
        f.close()

    def _writerecordsv2(self, records):
        """Write current state on disk in a version 2 file

        See the docstring for _readrecordsv2 for why we use 't'."""
        # these are the records that all version 2 clients can read
        allowlist = (RECORD_LOCAL, RECORD_OTHER, RECORD_MERGED)
        f = self._repo.vfs(self.statepathv2, b'wb')
        for key, data in records:
            assert len(key) == 1
            if key not in allowlist:
                key, data = RECORD_OVERRIDE, b'%s%s' % (key, data)
            format = b'>sI%is' % len(data)
            f.write(_pack(format, key, len(data), data))
        f.close()

    @staticmethod
    def getlocalkey(path):
        """hash the path of a local file context for storage in the .hg/merge
        directory."""

        return hex(hashutil.sha1(path).digest())

    def add(self, fcl, fco, fca, fd):
        """add a new (potentially?) conflicting file the merge state
        fcl: file context for local,
        fco: file context for remote,
        fca: file context for ancestors,
        fd:  file path of the resulting merge.

        note: also write the local version to the `.hg/merge` directory.
        """
        if fcl.isabsent():
            localkey = nullhex
        else:
            localkey = mergestate.getlocalkey(fcl.path())
            self._repo.vfs.write(b'merge/' + localkey, fcl.data())
        self._state[fd] = [
            MERGE_RECORD_UNRESOLVED,
            localkey,
            fcl.path(),
            fca.path(),
            hex(fca.filenode()),
            fco.path(),
            hex(fco.filenode()),
            fcl.flags(),
        ]
        self._stateextras[fd] = {b'ancestorlinknode': hex(fca.node())}
        self._dirty = True

    def addpath(self, path, frename, forigin):
        """add a new conflicting path to the merge state
        path:    the path that conflicts
        frename: the filename the conflicting file was renamed to
        forigin: origin of the file ('l' or 'r' for local/remote)
        """
        self._state[path] = [MERGE_RECORD_UNRESOLVED_PATH, frename, forigin]
        self._dirty = True

    def __contains__(self, dfile):
        return dfile in self._state

    def __getitem__(self, dfile):
        return self._state[dfile][0]

    def __iter__(self):
        return iter(sorted(self._state))

    def files(self):
        return self._state.keys()

    def mark(self, dfile, state):
        self._state[dfile][0] = state
        self._dirty = True

    def mdstate(self):
        return self._mdstate

    def unresolved(self):
        """Obtain the paths of unresolved files."""

        for f, entry in pycompat.iteritems(self._state):
            if entry[0] in (
                MERGE_RECORD_UNRESOLVED,
                MERGE_RECORD_UNRESOLVED_PATH,
            ):
                yield f

    def driverresolved(self):
        """Obtain the paths of driver-resolved files."""

        for f, entry in self._state.items():
            if entry[0] == MERGE_RECORD_DRIVER_RESOLVED:
                yield f

    def extras(self, filename):
        return self._stateextras.setdefault(filename, {})

    def _resolve(self, preresolve, dfile, wctx):
        """rerun merge process for file path `dfile`"""
        if self[dfile] in (MERGE_RECORD_RESOLVED, MERGE_RECORD_DRIVER_RESOLVED):
            return True, 0
        stateentry = self._state[dfile]
        state, localkey, lfile, afile, anode, ofile, onode, flags = stateentry
        octx = self._repo[self._other]
        extras = self.extras(dfile)
        anccommitnode = extras.get(b'ancestorlinknode')
        if anccommitnode:
            actx = self._repo[anccommitnode]
        else:
            actx = None
        fcd = self._filectxorabsent(localkey, wctx, dfile)
        fco = self._filectxorabsent(onode, octx, ofile)
        # TODO: move this to filectxorabsent
        fca = self._repo.filectx(afile, fileid=anode, changectx=actx)
        # "premerge" x flags
        flo = fco.flags()
        fla = fca.flags()
        if b'x' in flags + flo + fla and b'l' not in flags + flo + fla:
            if fca.node() == nullid and flags != flo:
                if preresolve:
                    self._repo.ui.warn(
                        _(
                            b'warning: cannot merge flags for %s '
                            b'without common ancestor - keeping local flags\n'
                        )
                        % afile
                    )
            elif flags == fla:
                flags = flo
        if preresolve:
            # restore local
            if localkey != nullhex:
                f = self._repo.vfs(b'merge/' + localkey)
                wctx[dfile].write(f.read(), flags)
                f.close()
            else:
                wctx[dfile].remove(ignoremissing=True)
            complete, r, deleted = filemerge.premerge(
                self._repo,
                wctx,
                self._local,
                lfile,
                fcd,
                fco,
                fca,
                labels=self._labels,
            )
        else:
            complete, r, deleted = filemerge.filemerge(
                self._repo,
                wctx,
                self._local,
                lfile,
                fcd,
                fco,
                fca,
                labels=self._labels,
            )
        if r is None:
            # no real conflict
            del self._state[dfile]
            self._stateextras.pop(dfile, None)
            self._dirty = True
        elif not r:
            self.mark(dfile, MERGE_RECORD_RESOLVED)

        if complete:
            action = None
            if deleted:
                if fcd.isabsent():
                    # dc: local picked. Need to drop if present, which may
                    # happen on re-resolves.
                    action = ACTION_FORGET
                else:
                    # cd: remote picked (or otherwise deleted)
                    action = ACTION_REMOVE
            else:
                if fcd.isabsent():  # dc: remote picked
                    action = ACTION_GET
                elif fco.isabsent():  # cd: local picked
                    if dfile in self.localctx:
                        action = ACTION_ADD_MODIFIED
                    else:
                        action = ACTION_ADD
                # else: regular merges (no action necessary)
            self._results[dfile] = r, action

        return complete, r

    def _filectxorabsent(self, hexnode, ctx, f):
        if hexnode == nullhex:
            return filemerge.absentfilectx(ctx, f)
        else:
            return ctx[f]

    def preresolve(self, dfile, wctx):
        """run premerge process for dfile

        Returns whether the merge is complete, and the exit code."""
        return self._resolve(True, dfile, wctx)

    def resolve(self, dfile, wctx):
        """run merge process (assuming premerge was run) for dfile

        Returns the exit code of the merge."""
        return self._resolve(False, dfile, wctx)[1]

    def counts(self):
        """return counts for updated, merged and removed files in this
        session"""
        updated, merged, removed = 0, 0, 0
        for r, action in pycompat.itervalues(self._results):
            if r is None:
                updated += 1
            elif r == 0:
                if action == ACTION_REMOVE:
                    removed += 1
                else:
                    merged += 1
        return updated, merged, removed

    def unresolvedcount(self):
        """get unresolved count for this merge (persistent)"""
        return len(list(self.unresolved()))

    def actions(self):
        """return lists of actions to perform on the dirstate"""
        actions = {
            ACTION_REMOVE: [],
            ACTION_FORGET: [],
            ACTION_ADD: [],
            ACTION_ADD_MODIFIED: [],
            ACTION_GET: [],
        }
        for f, (r, action) in pycompat.iteritems(self._results):
            if action is not None:
                actions[action].append((f, None, b"merge result"))
        return actions

    def recordactions(self):
        """record remove/add/get actions in the dirstate"""
        branchmerge = self._repo.dirstate.p2() != nullid
        recordupdates(self._repo, self.actions(), branchmerge, None)

    def queueremove(self, f):
        """queues a file to be removed from the dirstate

        Meant for use by custom merge drivers."""
        self._results[f] = 0, ACTION_REMOVE

    def queueadd(self, f):
        """queues a file to be added to the dirstate

        Meant for use by custom merge drivers."""
        self._results[f] = 0, ACTION_ADD

    def queueget(self, f):
        """queues a file to be marked modified in the dirstate

        Meant for use by custom merge drivers."""
        self._results[f] = 0, ACTION_GET


def _getcheckunknownconfig(repo, section, name):
    config = repo.ui.config(section, name)
    valid = [b'abort', b'ignore', b'warn']
    if config not in valid:
        validstr = b', '.join([b"'" + v + b"'" for v in valid])
        raise error.ConfigError(
            _(b"%s.%s not valid ('%s' is none of %s)")
            % (section, name, config, validstr)
        )
    return config


def _checkunknownfile(repo, wctx, mctx, f, f2=None):
    if wctx.isinmemory():
        # Nothing to do in IMM because nothing in the "working copy" can be an
        # unknown file.
        #
        # Note that we should bail out here, not in ``_checkunknownfiles()``,
        # because that function does other useful work.
        return False

    if f2 is None:
        f2 = f
    return (
        repo.wvfs.audit.check(f)
        and repo.wvfs.isfileorlink(f)
        and repo.dirstate.normalize(f) not in repo.dirstate
        and mctx[f2].cmp(wctx[f])
    )


class _unknowndirschecker(object):
    """
    Look for any unknown files or directories that may have a path conflict
    with a file.  If any path prefix of the file exists as a file or link,
    then it conflicts.  If the file itself is a directory that contains any
    file that is not tracked, then it conflicts.

    Returns the shortest path at which a conflict occurs, or None if there is
    no conflict.
    """

    def __init__(self):
        # A set of paths known to be good.  This prevents repeated checking of
        # dirs.  It will be updated with any new dirs that are checked and found
        # to be safe.
        self._unknowndircache = set()

        # A set of paths that are known to be absent.  This prevents repeated
        # checking of subdirectories that are known not to exist. It will be
        # updated with any new dirs that are checked and found to be absent.
        self._missingdircache = set()

    def __call__(self, repo, wctx, f):
        if wctx.isinmemory():
            # Nothing to do in IMM for the same reason as ``_checkunknownfile``.
            return False

        # Check for path prefixes that exist as unknown files.
        for p in reversed(list(pathutil.finddirs(f))):
            if p in self._missingdircache:
                return
            if p in self._unknowndircache:
                continue
            if repo.wvfs.audit.check(p):
                if (
                    repo.wvfs.isfileorlink(p)
                    and repo.dirstate.normalize(p) not in repo.dirstate
                ):
                    return p
                if not repo.wvfs.lexists(p):
                    self._missingdircache.add(p)
                    return
                self._unknowndircache.add(p)

        # Check if the file conflicts with a directory containing unknown files.
        if repo.wvfs.audit.check(f) and repo.wvfs.isdir(f):
            # Does the directory contain any files that are not in the dirstate?
            for p, dirs, files in repo.wvfs.walk(f):
                for fn in files:
                    relf = util.pconvert(repo.wvfs.reljoin(p, fn))
                    relf = repo.dirstate.normalize(relf, isknown=True)
                    if relf not in repo.dirstate:
                        return f
        return None


def _checkunknownfiles(repo, wctx, mctx, force, actions, mergeforce):
    """
    Considers any actions that care about the presence of conflicting unknown
    files. For some actions, the result is to abort; for others, it is to
    choose a different action.
    """
    fileconflicts = set()
    pathconflicts = set()
    warnconflicts = set()
    abortconflicts = set()
    unknownconfig = _getcheckunknownconfig(repo, b'merge', b'checkunknown')
    ignoredconfig = _getcheckunknownconfig(repo, b'merge', b'checkignored')
    pathconfig = repo.ui.configbool(
        b'experimental', b'merge.checkpathconflicts'
    )
    if not force:

        def collectconflicts(conflicts, config):
            if config == b'abort':
                abortconflicts.update(conflicts)
            elif config == b'warn':
                warnconflicts.update(conflicts)

        checkunknowndirs = _unknowndirschecker()
        for f, (m, args, msg) in pycompat.iteritems(actions):
            if m in (ACTION_CREATED, ACTION_DELETED_CHANGED):
                if _checkunknownfile(repo, wctx, mctx, f):
                    fileconflicts.add(f)
                elif pathconfig and f not in wctx:
                    path = checkunknowndirs(repo, wctx, f)
                    if path is not None:
                        pathconflicts.add(path)
            elif m == ACTION_LOCAL_DIR_RENAME_GET:
                if _checkunknownfile(repo, wctx, mctx, f, args[0]):
                    fileconflicts.add(f)

        allconflicts = fileconflicts | pathconflicts
        ignoredconflicts = {c for c in allconflicts if repo.dirstate._ignore(c)}
        unknownconflicts = allconflicts - ignoredconflicts
        collectconflicts(ignoredconflicts, ignoredconfig)
        collectconflicts(unknownconflicts, unknownconfig)
    else:
        for f, (m, args, msg) in pycompat.iteritems(actions):
            if m == ACTION_CREATED_MERGE:
                fl2, anc = args
                different = _checkunknownfile(repo, wctx, mctx, f)
                if repo.dirstate._ignore(f):
                    config = ignoredconfig
                else:
                    config = unknownconfig

                # The behavior when force is True is described by this table:
                #  config  different  mergeforce  |    action    backup
                #    *         n          *       |      get        n
                #    *         y          y       |     merge       -
                #   abort      y          n       |     merge       -   (1)
                #   warn       y          n       |  warn + get     y
                #  ignore      y          n       |      get        y
                #
                # (1) this is probably the wrong behavior here -- we should
                #     probably abort, but some actions like rebases currently
                #     don't like an abort happening in the middle of
                #     merge.update.
                if not different:
                    actions[f] = (ACTION_GET, (fl2, False), b'remote created')
                elif mergeforce or config == b'abort':
                    actions[f] = (
                        ACTION_MERGE,
                        (f, f, None, False, anc),
                        b'remote differs from untracked local',
                    )
                elif config == b'abort':
                    abortconflicts.add(f)
                else:
                    if config == b'warn':
                        warnconflicts.add(f)
                    actions[f] = (ACTION_GET, (fl2, True), b'remote created')

    for f in sorted(abortconflicts):
        warn = repo.ui.warn
        if f in pathconflicts:
            if repo.wvfs.isfileorlink(f):
                warn(_(b"%s: untracked file conflicts with directory\n") % f)
            else:
                warn(_(b"%s: untracked directory conflicts with file\n") % f)
        else:
            warn(_(b"%s: untracked file differs\n") % f)
    if abortconflicts:
        raise error.Abort(
            _(
                b"untracked files in working directory "
                b"differ from files in requested revision"
            )
        )

    for f in sorted(warnconflicts):
        if repo.wvfs.isfileorlink(f):
            repo.ui.warn(_(b"%s: replacing untracked file\n") % f)
        else:
            repo.ui.warn(_(b"%s: replacing untracked files in directory\n") % f)

    for f, (m, args, msg) in pycompat.iteritems(actions):
        if m == ACTION_CREATED:
            backup = (
                f in fileconflicts
                or f in pathconflicts
                or any(p in pathconflicts for p in pathutil.finddirs(f))
            )
            (flags,) = args
            actions[f] = (ACTION_GET, (flags, backup), msg)


def _forgetremoved(wctx, mctx, branchmerge):
    """
    Forget removed files

    If we're jumping between revisions (as opposed to merging), and if
    neither the working directory nor the target rev has the file,
    then we need to remove it from the dirstate, to prevent the
    dirstate from listing the file when it is no longer in the
    manifest.

    If we're merging, and the other revision has removed a file
    that is not present in the working directory, we need to mark it
    as removed.
    """

    actions = {}
    m = ACTION_FORGET
    if branchmerge:
        m = ACTION_REMOVE
    for f in wctx.deleted():
        if f not in mctx:
            actions[f] = m, None, b"forget deleted"

    if not branchmerge:
        for f in wctx.removed():
            if f not in mctx:
                actions[f] = ACTION_FORGET, None, b"forget removed"

    return actions


def _checkcollision(repo, wmf, actions):
    """
    Check for case-folding collisions.
    """

    # If the repo is narrowed, filter out files outside the narrowspec.
    narrowmatch = repo.narrowmatch()
    if not narrowmatch.always():
        wmf = wmf.matches(narrowmatch)
        if actions:
            narrowactions = {}
            for m, actionsfortype in pycompat.iteritems(actions):
                narrowactions[m] = []
                for (f, args, msg) in actionsfortype:
                    if narrowmatch(f):
                        narrowactions[m].append((f, args, msg))
            actions = narrowactions

    # build provisional merged manifest up
    pmmf = set(wmf)

    if actions:
        # KEEP and EXEC are no-op
        for m in (
            ACTION_ADD,
            ACTION_ADD_MODIFIED,
            ACTION_FORGET,
            ACTION_GET,
            ACTION_CHANGED_DELETED,
            ACTION_DELETED_CHANGED,
        ):
            for f, args, msg in actions[m]:
                pmmf.add(f)
        for f, args, msg in actions[ACTION_REMOVE]:
            pmmf.discard(f)
        for f, args, msg in actions[ACTION_DIR_RENAME_MOVE_LOCAL]:
            f2, flags = args
            pmmf.discard(f2)
            pmmf.add(f)
        for f, args, msg in actions[ACTION_LOCAL_DIR_RENAME_GET]:
            pmmf.add(f)
        for f, args, msg in actions[ACTION_MERGE]:
            f1, f2, fa, move, anc = args
            if move:
                pmmf.discard(f1)
            pmmf.add(f)

    # check case-folding collision in provisional merged manifest
    foldmap = {}
    for f in pmmf:
        fold = util.normcase(f)
        if fold in foldmap:
            raise error.Abort(
                _(b"case-folding collision between %s and %s")
                % (f, foldmap[fold])
            )
        foldmap[fold] = f

    # check case-folding of directories
    foldprefix = unfoldprefix = lastfull = b''
    for fold, f in sorted(foldmap.items()):
        if fold.startswith(foldprefix) and not f.startswith(unfoldprefix):
            # the folded prefix matches but actual casing is different
            raise error.Abort(
                _(b"case-folding collision between %s and directory of %s")
                % (lastfull, f)
            )
        foldprefix = fold + b'/'
        unfoldprefix = f + b'/'
        lastfull = f


def driverpreprocess(repo, ms, wctx, labels=None):
    """run the preprocess step of the merge driver, if any

    This is currently not implemented -- it's an extension point."""
    return True


def driverconclude(repo, ms, wctx, labels=None):
    """run the conclude step of the merge driver, if any

    This is currently not implemented -- it's an extension point."""
    return True


def _filesindirs(repo, manifest, dirs):
    """
    Generator that yields pairs of all the files in the manifest that are found
    inside the directories listed in dirs, and which directory they are found
    in.
    """
    for f in manifest:
        for p in pathutil.finddirs(f):
            if p in dirs:
                yield f, p
                break


def checkpathconflicts(repo, wctx, mctx, actions):
    """
    Check if any actions introduce path conflicts in the repository, updating
    actions to record or handle the path conflict accordingly.
    """
    mf = wctx.manifest()

    # The set of local files that conflict with a remote directory.
    localconflicts = set()

    # The set of directories that conflict with a remote file, and so may cause
    # conflicts if they still contain any files after the merge.
    remoteconflicts = set()

    # The set of directories that appear as both a file and a directory in the
    # remote manifest.  These indicate an invalid remote manifest, which
    # can't be updated to cleanly.
    invalidconflicts = set()

    # The set of directories that contain files that are being created.
    createdfiledirs = set()

    # The set of files deleted by all the actions.
    deletedfiles = set()

    for f, (m, args, msg) in actions.items():
        if m in (
            ACTION_CREATED,
            ACTION_DELETED_CHANGED,
            ACTION_MERGE,
            ACTION_CREATED_MERGE,
        ):
            # This action may create a new local file.
            createdfiledirs.update(pathutil.finddirs(f))
            if mf.hasdir(f):
                # The file aliases a local directory.  This might be ok if all
                # the files in the local directory are being deleted.  This
                # will be checked once we know what all the deleted files are.
                remoteconflicts.add(f)
        # Track the names of all deleted files.
        if m == ACTION_REMOVE:
            deletedfiles.add(f)
        if m == ACTION_MERGE:
            f1, f2, fa, move, anc = args
            if move:
                deletedfiles.add(f1)
        if m == ACTION_DIR_RENAME_MOVE_LOCAL:
            f2, flags = args
            deletedfiles.add(f2)

    # Check all directories that contain created files for path conflicts.
    for p in createdfiledirs:
        if p in mf:
            if p in mctx:
                # A file is in a directory which aliases both a local
                # and a remote file.  This is an internal inconsistency
                # within the remote manifest.
                invalidconflicts.add(p)
            else:
                # A file is in a directory which aliases a local file.
                # We will need to rename the local file.
                localconflicts.add(p)
        if p in actions and actions[p][0] in (
            ACTION_CREATED,
            ACTION_DELETED_CHANGED,
            ACTION_MERGE,
            ACTION_CREATED_MERGE,
        ):
            # The file is in a directory which aliases a remote file.
            # This is an internal inconsistency within the remote
            # manifest.
            invalidconflicts.add(p)

    # Rename all local conflicting files that have not been deleted.
    for p in localconflicts:
        if p not in deletedfiles:
            ctxname = bytes(wctx).rstrip(b'+')
            pnew = util.safename(p, ctxname, wctx, set(actions.keys()))
            actions[pnew] = (
                ACTION_PATH_CONFLICT_RESOLVE,
                (p,),
                b'local path conflict',
            )
            actions[p] = (ACTION_PATH_CONFLICT, (pnew, b'l'), b'path conflict')

    if remoteconflicts:
        # Check if all files in the conflicting directories have been removed.
        ctxname = bytes(mctx).rstrip(b'+')
        for f, p in _filesindirs(repo, mf, remoteconflicts):
            if f not in deletedfiles:
                m, args, msg = actions[p]
                pnew = util.safename(p, ctxname, wctx, set(actions.keys()))
                if m in (ACTION_DELETED_CHANGED, ACTION_MERGE):
                    # Action was merge, just update target.
                    actions[pnew] = (m, args, msg)
                else:
                    # Action was create, change to renamed get action.
                    fl = args[0]
                    actions[pnew] = (
                        ACTION_LOCAL_DIR_RENAME_GET,
                        (p, fl),
                        b'remote path conflict',
                    )
                actions[p] = (
                    ACTION_PATH_CONFLICT,
                    (pnew, ACTION_REMOVE),
                    b'path conflict',
                )
                remoteconflicts.remove(p)
                break

    if invalidconflicts:
        for p in invalidconflicts:
            repo.ui.warn(_(b"%s: is both a file and a directory\n") % p)
        raise error.Abort(_(b"destination manifest contains path conflicts"))


def _filternarrowactions(narrowmatch, branchmerge, actions):
    """
    Filters out actions that can ignored because the repo is narrowed.

    Raise an exception if the merge cannot be completed because the repo is
    narrowed.
    """
    nooptypes = {b'k'}  # TODO: handle with nonconflicttypes
    nonconflicttypes = set(b'a am c cm f g r e'.split())
    # We mutate the items in the dict during iteration, so iterate
    # over a copy.
    for f, action in list(actions.items()):
        if narrowmatch(f):
            pass
        elif not branchmerge:
            del actions[f]  # just updating, ignore changes outside clone
        elif action[0] in nooptypes:
            del actions[f]  # merge does not affect file
        elif action[0] in nonconflicttypes:
            raise error.Abort(
                _(
                    b'merge affects file \'%s\' outside narrow, '
                    b'which is not yet supported'
                )
                % f,
                hint=_(b'merging in the other direction may work'),
            )
        else:
            raise error.Abort(
                _(b'conflict in file \'%s\' is outside narrow clone') % f
            )


def manifestmerge(
    repo,
    wctx,
    p2,
    pa,
    branchmerge,
    force,
    matcher,
    acceptremote,
    followcopies,
    forcefulldiff=False,
):
    """
    Merge wctx and p2 with ancestor pa and generate merge action list

    branchmerge and force are as passed in to update
    matcher = matcher to filter file lists
    acceptremote = accept the incoming changes without prompting
    """
    if matcher is not None and matcher.always():
        matcher = None

    copy, movewithdir, diverge, renamedelete, dirmove = {}, {}, {}, {}, {}

    # manifests fetched in order are going to be faster, so prime the caches
    [
        x.manifest()
        for x in sorted(wctx.parents() + [p2, pa], key=scmutil.intrev)
    ]

    if followcopies:
        ret = copies.mergecopies(repo, wctx, p2, pa)
        copy, movewithdir, diverge, renamedelete, dirmove = ret

    boolbm = pycompat.bytestr(bool(branchmerge))
    boolf = pycompat.bytestr(bool(force))
    boolm = pycompat.bytestr(bool(matcher))
    repo.ui.note(_(b"resolving manifests\n"))
    repo.ui.debug(
        b" branchmerge: %s, force: %s, partial: %s\n" % (boolbm, boolf, boolm)
    )
    repo.ui.debug(b" ancestor: %s, local: %s, remote: %s\n" % (pa, wctx, p2))

    m1, m2, ma = wctx.manifest(), p2.manifest(), pa.manifest()
    copied = set(copy.values())
    copied.update(movewithdir.values())

    if b'.hgsubstate' in m1 and wctx.rev() is None:
        # Check whether sub state is modified, and overwrite the manifest
        # to flag the change. If wctx is a committed revision, we shouldn't
        # care for the dirty state of the working directory.
        if any(wctx.sub(s).dirty() for s in wctx.substate):
            m1[b'.hgsubstate'] = modifiednodeid

    # Don't use m2-vs-ma optimization if:
    # - ma is the same as m1 or m2, which we're just going to diff again later
    # - The caller specifically asks for a full diff, which is useful during bid
    #   merge.
    if pa not in ([wctx, p2] + wctx.parents()) and not forcefulldiff:
        # Identify which files are relevant to the merge, so we can limit the
        # total m1-vs-m2 diff to just those files. This has significant
        # performance benefits in large repositories.
        relevantfiles = set(ma.diff(m2).keys())

        # For copied and moved files, we need to add the source file too.
        for copykey, copyvalue in pycompat.iteritems(copy):
            if copyvalue in relevantfiles:
                relevantfiles.add(copykey)
        for movedirkey in movewithdir:
            relevantfiles.add(movedirkey)
        filesmatcher = scmutil.matchfiles(repo, relevantfiles)
        matcher = matchmod.intersectmatchers(matcher, filesmatcher)

    diff = m1.diff(m2, match=matcher)

    actions = {}
    for f, ((n1, fl1), (n2, fl2)) in pycompat.iteritems(diff):
        if n1 and n2:  # file exists on both local and remote side
            if f not in ma:
                fa = copy.get(f, None)
                if fa is not None:
                    actions[f] = (
                        ACTION_MERGE,
                        (f, f, fa, False, pa.node()),
                        b'both renamed from %s' % fa,
                    )
                else:
                    actions[f] = (
                        ACTION_MERGE,
                        (f, f, None, False, pa.node()),
                        b'both created',
                    )
            else:
                a = ma[f]
                fla = ma.flags(f)
                nol = b'l' not in fl1 + fl2 + fla
                if n2 == a and fl2 == fla:
                    actions[f] = (ACTION_KEEP, (), b'remote unchanged')
                elif n1 == a and fl1 == fla:  # local unchanged - use remote
                    if n1 == n2:  # optimization: keep local content
                        actions[f] = (
                            ACTION_EXEC,
                            (fl2,),
                            b'update permissions',
                        )
                    else:
                        actions[f] = (
                            ACTION_GET,
                            (fl2, False),
                            b'remote is newer',
                        )
                elif nol and n2 == a:  # remote only changed 'x'
                    actions[f] = (ACTION_EXEC, (fl2,), b'update permissions')
                elif nol and n1 == a:  # local only changed 'x'
                    actions[f] = (ACTION_GET, (fl1, False), b'remote is newer')
                else:  # both changed something
                    actions[f] = (
                        ACTION_MERGE,
                        (f, f, f, False, pa.node()),
                        b'versions differ',
                    )
        elif n1:  # file exists only on local side
            if f in copied:
                pass  # we'll deal with it on m2 side
            elif f in movewithdir:  # directory rename, move local
                f2 = movewithdir[f]
                if f2 in m2:
                    actions[f2] = (
                        ACTION_MERGE,
                        (f, f2, None, True, pa.node()),
                        b'remote directory rename, both created',
                    )
                else:
                    actions[f2] = (
                        ACTION_DIR_RENAME_MOVE_LOCAL,
                        (f, fl1),
                        b'remote directory rename - move from %s' % f,
                    )
            elif f in copy:
                f2 = copy[f]
                actions[f] = (
                    ACTION_MERGE,
                    (f, f2, f2, False, pa.node()),
                    b'local copied/moved from %s' % f2,
                )
            elif f in ma:  # clean, a different, no remote
                if n1 != ma[f]:
                    if acceptremote:
                        actions[f] = (ACTION_REMOVE, None, b'remote delete')
                    else:
                        actions[f] = (
                            ACTION_CHANGED_DELETED,
                            (f, None, f, False, pa.node()),
                            b'prompt changed/deleted',
                        )
                elif n1 == addednodeid:
                    # This extra 'a' is added by working copy manifest to mark
                    # the file as locally added. We should forget it instead of
                    # deleting it.
                    actions[f] = (ACTION_FORGET, None, b'remote deleted')
                else:
                    actions[f] = (ACTION_REMOVE, None, b'other deleted')
        elif n2:  # file exists only on remote side
            if f in copied:
                pass  # we'll deal with it on m1 side
            elif f in movewithdir:
                f2 = movewithdir[f]
                if f2 in m1:
                    actions[f2] = (
                        ACTION_MERGE,
                        (f2, f, None, False, pa.node()),
                        b'local directory rename, both created',
                    )
                else:
                    actions[f2] = (
                        ACTION_LOCAL_DIR_RENAME_GET,
                        (f, fl2),
                        b'local directory rename - get from %s' % f,
                    )
            elif f in copy:
                f2 = copy[f]
                if f2 in m2:
                    actions[f] = (
                        ACTION_MERGE,
                        (f2, f, f2, False, pa.node()),
                        b'remote copied from %s' % f2,
                    )
                else:
                    actions[f] = (
                        ACTION_MERGE,
                        (f2, f, f2, True, pa.node()),
                        b'remote moved from %s' % f2,
                    )
            elif f not in ma:
                # local unknown, remote created: the logic is described by the
                # following table:
                #
                # force  branchmerge  different  |  action
                #   n         *           *      |   create
                #   y         n           *      |   create
                #   y         y           n      |   create
                #   y         y           y      |   merge
                #
                # Checking whether the files are different is expensive, so we
                # don't do that when we can avoid it.
                if not force:
                    actions[f] = (ACTION_CREATED, (fl2,), b'remote created')
                elif not branchmerge:
                    actions[f] = (ACTION_CREATED, (fl2,), b'remote created')
                else:
                    actions[f] = (
                        ACTION_CREATED_MERGE,
                        (fl2, pa.node()),
                        b'remote created, get or merge',
                    )
            elif n2 != ma[f]:
                df = None
                for d in dirmove:
                    if f.startswith(d):
                        # new file added in a directory that was moved
                        df = dirmove[d] + f[len(d) :]
                        break
                if df is not None and df in m1:
                    actions[df] = (
                        ACTION_MERGE,
                        (df, f, f, False, pa.node()),
                        b'local directory rename - respect move '
                        b'from %s' % f,
                    )
                elif acceptremote:
                    actions[f] = (ACTION_CREATED, (fl2,), b'remote recreating')
                else:
                    actions[f] = (
                        ACTION_DELETED_CHANGED,
                        (None, f, f, False, pa.node()),
                        b'prompt deleted/changed',
                    )

    if repo.ui.configbool(b'experimental', b'merge.checkpathconflicts'):
        # If we are merging, look for path conflicts.
        checkpathconflicts(repo, wctx, p2, actions)

    narrowmatch = repo.narrowmatch()
    if not narrowmatch.always():
        # Updates "actions" in place
        _filternarrowactions(narrowmatch, branchmerge, actions)

    return actions, diverge, renamedelete


def _resolvetrivial(repo, wctx, mctx, ancestor, actions):
    """Resolves false conflicts where the nodeid changed but the content
       remained the same."""
    # We force a copy of actions.items() because we're going to mutate
    # actions as we resolve trivial conflicts.
    for f, (m, args, msg) in list(actions.items()):
        if (
            m == ACTION_CHANGED_DELETED
            and f in ancestor
            and not wctx[f].cmp(ancestor[f])
        ):
            # local did change but ended up with same content
            actions[f] = ACTION_REMOVE, None, b'prompt same'
        elif (
            m == ACTION_DELETED_CHANGED
            and f in ancestor
            and not mctx[f].cmp(ancestor[f])
        ):
            # remote did change but ended up with same content
            del actions[f]  # don't get = keep local deleted


def calculateupdates(
    repo,
    wctx,
    mctx,
    ancestors,
    branchmerge,
    force,
    acceptremote,
    followcopies,
    matcher=None,
    mergeforce=False,
):
    """Calculate the actions needed to merge mctx into wctx using ancestors"""
    # Avoid cycle.
    from . import sparse

    if len(ancestors) == 1:  # default
        actions, diverge, renamedelete = manifestmerge(
            repo,
            wctx,
            mctx,
            ancestors[0],
            branchmerge,
            force,
            matcher,
            acceptremote,
            followcopies,
        )
        _checkunknownfiles(repo, wctx, mctx, force, actions, mergeforce)

    else:  # only when merge.preferancestor=* - the default
        repo.ui.note(
            _(b"note: merging %s and %s using bids from ancestors %s\n")
            % (
                wctx,
                mctx,
                _(b' and ').join(pycompat.bytestr(anc) for anc in ancestors),
            )
        )

        # Call for bids
        fbids = (
            {}
        )  # mapping filename to bids (action method to list af actions)
        diverge, renamedelete = None, None
        for ancestor in ancestors:
            repo.ui.note(_(b'\ncalculating bids for ancestor %s\n') % ancestor)
            actions, diverge1, renamedelete1 = manifestmerge(
                repo,
                wctx,
                mctx,
                ancestor,
                branchmerge,
                force,
                matcher,
                acceptremote,
                followcopies,
                forcefulldiff=True,
            )
            _checkunknownfiles(repo, wctx, mctx, force, actions, mergeforce)

            # Track the shortest set of warning on the theory that bid
            # merge will correctly incorporate more information
            if diverge is None or len(diverge1) < len(diverge):
                diverge = diverge1
            if renamedelete is None or len(renamedelete) < len(renamedelete1):
                renamedelete = renamedelete1

            for f, a in sorted(pycompat.iteritems(actions)):
                m, args, msg = a
                repo.ui.debug(b' %s: %s -> %s\n' % (f, msg, m))
                if f in fbids:
                    d = fbids[f]
                    if m in d:
                        d[m].append(a)
                    else:
                        d[m] = [a]
                else:
                    fbids[f] = {m: [a]}

        # Pick the best bid for each file
        repo.ui.note(_(b'\nauction for merging merge bids\n'))
        actions = {}
        for f, bids in sorted(fbids.items()):
            # bids is a mapping from action method to list af actions
            # Consensus?
            if len(bids) == 1:  # all bids are the same kind of method
                m, l = list(bids.items())[0]
                if all(a == l[0] for a in l[1:]):  # len(bids) is > 1
                    repo.ui.note(_(b" %s: consensus for %s\n") % (f, m))
                    actions[f] = l[0]
                    continue
            # If keep is an option, just do it.
            if ACTION_KEEP in bids:
                repo.ui.note(_(b" %s: picking 'keep' action\n") % f)
                actions[f] = bids[ACTION_KEEP][0]
                continue
            # If there are gets and they all agree [how could they not?], do it.
            if ACTION_GET in bids:
                ga0 = bids[ACTION_GET][0]
                if all(a == ga0 for a in bids[ACTION_GET][1:]):
                    repo.ui.note(_(b" %s: picking 'get' action\n") % f)
                    actions[f] = ga0
                    continue
            # TODO: Consider other simple actions such as mode changes
            # Handle inefficient democrazy.
            repo.ui.note(_(b' %s: multiple bids for merge action:\n') % f)
            for m, l in sorted(bids.items()):
                for _f, args, msg in l:
                    repo.ui.note(b'  %s -> %s\n' % (msg, m))
            # Pick random action. TODO: Instead, prompt user when resolving
            m, l = list(bids.items())[0]
            repo.ui.warn(
                _(b' %s: ambiguous merge - picked %s action\n') % (f, m)
            )
            actions[f] = l[0]
            continue
        repo.ui.note(_(b'end of auction\n\n'))

    if wctx.rev() is None:
        fractions = _forgetremoved(wctx, mctx, branchmerge)
        actions.update(fractions)

    prunedactions = sparse.filterupdatesactions(
        repo, wctx, mctx, branchmerge, actions
    )
    _resolvetrivial(repo, wctx, mctx, ancestors[0], actions)

    return prunedactions, diverge, renamedelete


def _getcwd():
    try:
        return encoding.getcwd()
    except OSError as err:
        if err.errno == errno.ENOENT:
            return None
        raise


def batchremove(repo, wctx, actions):
    """apply removes to the working directory

    yields tuples for progress updates
    """
    verbose = repo.ui.verbose
    cwd = _getcwd()
    i = 0
    for f, args, msg in actions:
        repo.ui.debug(b" %s: %s -> r\n" % (f, msg))
        if verbose:
            repo.ui.note(_(b"removing %s\n") % f)
        wctx[f].audit()
        try:
            wctx[f].remove(ignoremissing=True)
        except OSError as inst:
            repo.ui.warn(
                _(b"update failed to remove %s: %s!\n") % (f, inst.strerror)
            )
        if i == 100:
            yield i, f
            i = 0
        i += 1
    if i > 0:
        yield i, f

    if cwd and not _getcwd():
        # cwd was removed in the course of removing files; print a helpful
        # warning.
        repo.ui.warn(
            _(
                b"current directory was removed\n"
                b"(consider changing to repo root: %s)\n"
            )
            % repo.root
        )


def batchget(repo, mctx, wctx, wantfiledata, actions):
    """apply gets to the working directory

    mctx is the context to get from

    Yields arbitrarily many (False, tuple) for progress updates, followed by
    exactly one (True, filedata). When wantfiledata is false, filedata is an
    empty dict. When wantfiledata is true, filedata[f] is a triple (mode, size,
    mtime) of the file f written for each action.
    """
    filedata = {}
    verbose = repo.ui.verbose
    fctx = mctx.filectx
    ui = repo.ui
    i = 0
    with repo.wvfs.backgroundclosing(ui, expectedcount=len(actions)):
        for f, (flags, backup), msg in actions:
            repo.ui.debug(b" %s: %s -> g\n" % (f, msg))
            if verbose:
                repo.ui.note(_(b"getting %s\n") % f)

            if backup:
                # If a file or directory exists with the same name, back that
                # up.  Otherwise, look to see if there is a file that conflicts
                # with a directory this file is in, and if so, back that up.
                conflicting = f
                if not repo.wvfs.lexists(f):
                    for p in pathutil.finddirs(f):
                        if repo.wvfs.isfileorlink(p):
                            conflicting = p
                            break
                if repo.wvfs.lexists(conflicting):
                    orig = scmutil.backuppath(ui, repo, conflicting)
                    util.rename(repo.wjoin(conflicting), orig)
            wfctx = wctx[f]
            wfctx.clearunknown()
            atomictemp = ui.configbool(b"experimental", b"update.atomic-file")
            size = wfctx.write(
                fctx(f).data(),
                flags,
                backgroundclose=True,
                atomictemp=atomictemp,
            )
            if wantfiledata:
                s = wfctx.lstat()
                mode = s.st_mode
                mtime = s[stat.ST_MTIME]
                filedata[f] = (mode, size, mtime)  # for dirstate.normal
            if i == 100:
                yield False, (i, f)
                i = 0
            i += 1
    if i > 0:
        yield False, (i, f)
    yield True, filedata


def _prefetchfiles(repo, ctx, actions):
    """Invoke ``scmutil.prefetchfiles()`` for the files relevant to the dict
    of merge actions.  ``ctx`` is the context being merged in."""

    # Skipping 'a', 'am', 'f', 'r', 'dm', 'e', 'k', 'p' and 'pr', because they
    # don't touch the context to be merged in.  'cd' is skipped, because
    # changed/deleted never resolves to something from the remote side.
    oplist = [
        actions[a]
        for a in (
            ACTION_GET,
            ACTION_DELETED_CHANGED,
            ACTION_LOCAL_DIR_RENAME_GET,
            ACTION_MERGE,
        )
    ]
    prefetch = scmutil.prefetchfiles
    matchfiles = scmutil.matchfiles
    prefetch(
        repo,
        [ctx.rev()],
        matchfiles(repo, [f for sublist in oplist for f, args, msg in sublist]),
    )


@attr.s(frozen=True)
class updateresult(object):
    updatedcount = attr.ib()
    mergedcount = attr.ib()
    removedcount = attr.ib()
    unresolvedcount = attr.ib()

    def isempty(self):
        return not (
            self.updatedcount
            or self.mergedcount
            or self.removedcount
            or self.unresolvedcount
        )


def emptyactions():
    """create an actions dict, to be populated and passed to applyupdates()"""
    return dict(
        (m, [])
        for m in (
            ACTION_ADD,
            ACTION_ADD_MODIFIED,
            ACTION_FORGET,
            ACTION_GET,
            ACTION_CHANGED_DELETED,
            ACTION_DELETED_CHANGED,
            ACTION_REMOVE,
            ACTION_DIR_RENAME_MOVE_LOCAL,
            ACTION_LOCAL_DIR_RENAME_GET,
            ACTION_MERGE,
            ACTION_EXEC,
            ACTION_KEEP,
            ACTION_PATH_CONFLICT,
            ACTION_PATH_CONFLICT_RESOLVE,
        )
    )


def applyupdates(
    repo, actions, wctx, mctx, overwrite, wantfiledata, labels=None
):
    """apply the merge action list to the working directory

    wctx is the working copy context
    mctx is the context to be merged into the working copy

    Return a tuple of (counts, filedata), where counts is a tuple
    (updated, merged, removed, unresolved) that describes how many
    files were affected by the update, and filedata is as described in
    batchget.
    """

    _prefetchfiles(repo, mctx, actions)

    updated, merged, removed = 0, 0, 0
    ms = mergestate.clean(repo, wctx.p1().node(), mctx.node(), labels)
    moves = []
    for m, l in actions.items():
        l.sort()

    # 'cd' and 'dc' actions are treated like other merge conflicts
    mergeactions = sorted(actions[ACTION_CHANGED_DELETED])
    mergeactions.extend(sorted(actions[ACTION_DELETED_CHANGED]))
    mergeactions.extend(actions[ACTION_MERGE])
    for f, args, msg in mergeactions:
        f1, f2, fa, move, anc = args
        if f == b'.hgsubstate':  # merged internally
            continue
        if f1 is None:
            fcl = filemerge.absentfilectx(wctx, fa)
        else:
            repo.ui.debug(b" preserving %s for resolve of %s\n" % (f1, f))
            fcl = wctx[f1]
        if f2 is None:
            fco = filemerge.absentfilectx(mctx, fa)
        else:
            fco = mctx[f2]
        actx = repo[anc]
        if fa in actx:
            fca = actx[fa]
        else:
            # TODO: move to absentfilectx
            fca = repo.filectx(f1, fileid=nullrev)
        ms.add(fcl, fco, fca, f)
        if f1 != f and move:
            moves.append(f1)

    # remove renamed files after safely stored
    for f in moves:
        if wctx[f].lexists():
            repo.ui.debug(b"removing %s\n" % f)
            wctx[f].audit()
            wctx[f].remove()

    numupdates = sum(len(l) for m, l in actions.items() if m != ACTION_KEEP)
    progress = repo.ui.makeprogress(
        _(b'updating'), unit=_(b'files'), total=numupdates
    )

    if [a for a in actions[ACTION_REMOVE] if a[0] == b'.hgsubstate']:
        subrepoutil.submerge(repo, wctx, mctx, wctx, overwrite, labels)

    # record path conflicts
    for f, args, msg in actions[ACTION_PATH_CONFLICT]:
        f1, fo = args
        s = repo.ui.status
        s(
            _(
                b"%s: path conflict - a file or link has the same name as a "
                b"directory\n"
            )
            % f
        )
        if fo == b'l':
            s(_(b"the local file has been renamed to %s\n") % f1)
        else:
            s(_(b"the remote file has been renamed to %s\n") % f1)
        s(_(b"resolve manually then use 'hg resolve --mark %s'\n") % f)
        ms.addpath(f, f1, fo)
        progress.increment(item=f)

    # When merging in-memory, we can't support worker processes, so set the
    # per-item cost at 0 in that case.
    cost = 0 if wctx.isinmemory() else 0.001

    # remove in parallel (must come before resolving path conflicts and getting)
    prog = worker.worker(
        repo.ui, cost, batchremove, (repo, wctx), actions[ACTION_REMOVE]
    )
    for i, item in prog:
        progress.increment(step=i, item=item)
    removed = len(actions[ACTION_REMOVE])

    # resolve path conflicts (must come before getting)
    for f, args, msg in actions[ACTION_PATH_CONFLICT_RESOLVE]:
        repo.ui.debug(b" %s: %s -> pr\n" % (f, msg))
        (f0,) = args
        if wctx[f0].lexists():
            repo.ui.note(_(b"moving %s to %s\n") % (f0, f))
            wctx[f].audit()
            wctx[f].write(wctx.filectx(f0).data(), wctx.filectx(f0).flags())
            wctx[f0].remove()
        progress.increment(item=f)

    # get in parallel.
    threadsafe = repo.ui.configbool(
        b'experimental', b'worker.wdir-get-thread-safe'
    )
    prog = worker.worker(
        repo.ui,
        cost,
        batchget,
        (repo, mctx, wctx, wantfiledata),
        actions[ACTION_GET],
        threadsafe=threadsafe,
        hasretval=True,
    )
    getfiledata = {}
    for final, res in prog:
        if final:
            getfiledata = res
        else:
            i, item = res
            progress.increment(step=i, item=item)
    updated = len(actions[ACTION_GET])

    if [a for a in actions[ACTION_GET] if a[0] == b'.hgsubstate']:
        subrepoutil.submerge(repo, wctx, mctx, wctx, overwrite, labels)

    # forget (manifest only, just log it) (must come first)
    for f, args, msg in actions[ACTION_FORGET]:
        repo.ui.debug(b" %s: %s -> f\n" % (f, msg))
        progress.increment(item=f)

    # re-add (manifest only, just log it)
    for f, args, msg in actions[ACTION_ADD]:
        repo.ui.debug(b" %s: %s -> a\n" % (f, msg))
        progress.increment(item=f)

    # re-add/mark as modified (manifest only, just log it)
    for f, args, msg in actions[ACTION_ADD_MODIFIED]:
        repo.ui.debug(b" %s: %s -> am\n" % (f, msg))
        progress.increment(item=f)

    # keep (noop, just log it)
    for f, args, msg in actions[ACTION_KEEP]:
        repo.ui.debug(b" %s: %s -> k\n" % (f, msg))
        # no progress

    # directory rename, move local
    for f, args, msg in actions[ACTION_DIR_RENAME_MOVE_LOCAL]:
        repo.ui.debug(b" %s: %s -> dm\n" % (f, msg))
        progress.increment(item=f)
        f0, flags = args
        repo.ui.note(_(b"moving %s to %s\n") % (f0, f))
        wctx[f].audit()
        wctx[f].write(wctx.filectx(f0).data(), flags)
        wctx[f0].remove()
        updated += 1

    # local directory rename, get
    for f, args, msg in actions[ACTION_LOCAL_DIR_RENAME_GET]:
        repo.ui.debug(b" %s: %s -> dg\n" % (f, msg))
        progress.increment(item=f)
        f0, flags = args
        repo.ui.note(_(b"getting %s to %s\n") % (f0, f))
        wctx[f].write(mctx.filectx(f0).data(), flags)
        updated += 1

    # exec
    for f, args, msg in actions[ACTION_EXEC]:
        repo.ui.debug(b" %s: %s -> e\n" % (f, msg))
        progress.increment(item=f)
        (flags,) = args
        wctx[f].audit()
        wctx[f].setflags(b'l' in flags, b'x' in flags)
        updated += 1

    # the ordering is important here -- ms.mergedriver will raise if the merge
    # driver has changed, and we want to be able to bypass it when overwrite is
    # True
    usemergedriver = not overwrite and mergeactions and ms.mergedriver

    if usemergedriver:
        if wctx.isinmemory():
            raise error.InMemoryMergeConflictsError(
                b"in-memory merge does not support mergedriver"
            )
        ms.commit()
        proceed = driverpreprocess(repo, ms, wctx, labels=labels)
        # the driver might leave some files unresolved
        unresolvedf = set(ms.unresolved())
        if not proceed:
            # XXX setting unresolved to at least 1 is a hack to make sure we
            # error out
            return updateresult(
                updated, merged, removed, max(len(unresolvedf), 1)
            )
        newactions = []
        for f, args, msg in mergeactions:
            if f in unresolvedf:
                newactions.append((f, args, msg))
        mergeactions = newactions

    try:
        # premerge
        tocomplete = []
        for f, args, msg in mergeactions:
            repo.ui.debug(b" %s: %s -> m (premerge)\n" % (f, msg))
            progress.increment(item=f)
            if f == b'.hgsubstate':  # subrepo states need updating
                subrepoutil.submerge(
                    repo, wctx, mctx, wctx.ancestor(mctx), overwrite, labels
                )
                continue
            wctx[f].audit()
            complete, r = ms.preresolve(f, wctx)
            if not complete:
                numupdates += 1
                tocomplete.append((f, args, msg))

        # merge
        for f, args, msg in tocomplete:
            repo.ui.debug(b" %s: %s -> m (merge)\n" % (f, msg))
            progress.increment(item=f, total=numupdates)
            ms.resolve(f, wctx)

    finally:
        ms.commit()

    unresolved = ms.unresolvedcount()

    if (
        usemergedriver
        and not unresolved
        and ms.mdstate() != MERGE_DRIVER_STATE_SUCCESS
    ):
        if not driverconclude(repo, ms, wctx, labels=labels):
            # XXX setting unresolved to at least 1 is a hack to make sure we
            # error out
            unresolved = max(unresolved, 1)

        ms.commit()

    msupdated, msmerged, msremoved = ms.counts()
    updated += msupdated
    merged += msmerged
    removed += msremoved

    extraactions = ms.actions()
    if extraactions:
        mfiles = set(a[0] for a in actions[ACTION_MERGE])
        for k, acts in pycompat.iteritems(extraactions):
            actions[k].extend(acts)
            if k == ACTION_GET and wantfiledata:
                # no filedata until mergestate is updated to provide it
                for a in acts:
                    getfiledata[a[0]] = None
            # Remove these files from actions[ACTION_MERGE] as well. This is
            # important because in recordupdates, files in actions[ACTION_MERGE]
            # are processed after files in other actions, and the merge driver
            # might add files to those actions via extraactions above. This can
            # lead to a file being recorded twice, with poor results. This is
            # especially problematic for actions[ACTION_REMOVE] (currently only
            # possible with the merge driver in the initial merge process;
            # interrupted merges don't go through this flow).
            #
            # The real fix here is to have indexes by both file and action so
            # that when the action for a file is changed it is automatically
            # reflected in the other action lists. But that involves a more
            # complex data structure, so this will do for now.
            #
            # We don't need to do the same operation for 'dc' and 'cd' because
            # those lists aren't consulted again.
            mfiles.difference_update(a[0] for a in acts)

        actions[ACTION_MERGE] = [
            a for a in actions[ACTION_MERGE] if a[0] in mfiles
        ]

    progress.complete()
    assert len(getfiledata) == (len(actions[ACTION_GET]) if wantfiledata else 0)
    return updateresult(updated, merged, removed, unresolved), getfiledata


def recordupdates(repo, actions, branchmerge, getfiledata):
    """record merge actions to the dirstate"""
    # remove (must come first)
    for f, args, msg in actions.get(ACTION_REMOVE, []):
        if branchmerge:
            repo.dirstate.remove(f)
        else:
            repo.dirstate.drop(f)

    # forget (must come first)
    for f, args, msg in actions.get(ACTION_FORGET, []):
        repo.dirstate.drop(f)

    # resolve path conflicts
    for f, args, msg in actions.get(ACTION_PATH_CONFLICT_RESOLVE, []):
        (f0,) = args
        origf0 = repo.dirstate.copied(f0) or f0
        repo.dirstate.add(f)
        repo.dirstate.copy(origf0, f)
        if f0 == origf0:
            repo.dirstate.remove(f0)
        else:
            repo.dirstate.drop(f0)

    # re-add
    for f, args, msg in actions.get(ACTION_ADD, []):
        repo.dirstate.add(f)

    # re-add/mark as modified
    for f, args, msg in actions.get(ACTION_ADD_MODIFIED, []):
        if branchmerge:
            repo.dirstate.normallookup(f)
        else:
            repo.dirstate.add(f)

    # exec change
    for f, args, msg in actions.get(ACTION_EXEC, []):
        repo.dirstate.normallookup(f)

    # keep
    for f, args, msg in actions.get(ACTION_KEEP, []):
        pass

    # get
    for f, args, msg in actions.get(ACTION_GET, []):
        if branchmerge:
            repo.dirstate.otherparent(f)
        else:
            parentfiledata = getfiledata[f] if getfiledata else None
            repo.dirstate.normal(f, parentfiledata=parentfiledata)

    # merge
    for f, args, msg in actions.get(ACTION_MERGE, []):
        f1, f2, fa, move, anc = args
        if branchmerge:
            # We've done a branch merge, mark this file as merged
            # so that we properly record the merger later
            repo.dirstate.merge(f)
            if f1 != f2:  # copy/rename
                if move:
                    repo.dirstate.remove(f1)
                if f1 != f:
                    repo.dirstate.copy(f1, f)
                else:
                    repo.dirstate.copy(f2, f)
        else:
            # We've update-merged a locally modified file, so
            # we set the dirstate to emulate a normal checkout
            # of that file some time in the past. Thus our
            # merge will appear as a normal local file
            # modification.
            if f2 == f:  # file not locally copied/moved
                repo.dirstate.normallookup(f)
            if move:
                repo.dirstate.drop(f1)

    # directory rename, move local
    for f, args, msg in actions.get(ACTION_DIR_RENAME_MOVE_LOCAL, []):
        f0, flag = args
        if branchmerge:
            repo.dirstate.add(f)
            repo.dirstate.remove(f0)
            repo.dirstate.copy(f0, f)
        else:
            repo.dirstate.normal(f)
            repo.dirstate.drop(f0)

    # directory rename, get
    for f, args, msg in actions.get(ACTION_LOCAL_DIR_RENAME_GET, []):
        f0, flag = args
        if branchmerge:
            repo.dirstate.add(f)
            repo.dirstate.copy(f0, f)
        else:
            repo.dirstate.normal(f)


UPDATECHECK_ABORT = b'abort'  # handled at higher layers
UPDATECHECK_NONE = b'none'
UPDATECHECK_LINEAR = b'linear'
UPDATECHECK_NO_CONFLICT = b'noconflict'


def update(
    repo,
    node,
    branchmerge,
    force,
    ancestor=None,
    mergeancestor=False,
    labels=None,
    matcher=None,
    mergeforce=False,
    updatecheck=None,
    wc=None,
):
    """
    Perform a merge between the working directory and the given node

    node = the node to update to
    branchmerge = whether to merge between branches
    force = whether to force branch merging or file overwriting
    matcher = a matcher to filter file lists (dirstate not updated)
    mergeancestor = whether it is merging with an ancestor. If true,
      we should accept the incoming changes for any prompts that occur.
      If false, merging with an ancestor (fast-forward) is only allowed
      between different named branches. This flag is used by rebase extension
      as a temporary fix and should be avoided in general.
    labels = labels to use for base, local and other
    mergeforce = whether the merge was run with 'merge --force' (deprecated): if
      this is True, then 'force' should be True as well.

    The table below shows all the behaviors of the update command given the
    -c/--check and -C/--clean or no options, whether the working directory is
    dirty, whether a revision is specified, and the relationship of the parent
    rev to the target rev (linear or not). Match from top first. The -n
    option doesn't exist on the command line, but represents the
    experimental.updatecheck=noconflict option.

    This logic is tested by test-update-branches.t.

    -c  -C  -n  -m  dirty  rev  linear  |  result
     y   y   *   *    *     *     *     |    (1)
     y   *   y   *    *     *     *     |    (1)
     y   *   *   y    *     *     *     |    (1)
     *   y   y   *    *     *     *     |    (1)
     *   y   *   y    *     *     *     |    (1)
     *   *   y   y    *     *     *     |    (1)
     *   *   *   *    *     n     n     |     x
     *   *   *   *    n     *     *     |    ok
     n   n   n   n    y     *     y     |   merge
     n   n   n   n    y     y     n     |    (2)
     n   n   n   y    y     *     *     |   merge
     n   n   y   n    y     *     *     |  merge if no conflict
     n   y   n   n    y     *     *     |  discard
     y   n   n   n    y     *     *     |    (3)

    x = can't happen
    * = don't-care
    1 = incompatible options (checked in commands.py)
    2 = abort: uncommitted changes (commit or update --clean to discard changes)
    3 = abort: uncommitted changes (checked in commands.py)

    The merge is performed inside ``wc``, a workingctx-like objects. It defaults
    to repo[None] if None is passed.

    Return the same tuple as applyupdates().
    """
    # Avoid cycle.
    from . import sparse

    # This function used to find the default destination if node was None, but
    # that's now in destutil.py.
    assert node is not None
    if not branchmerge and not force:
        # TODO: remove the default once all callers that pass branchmerge=False
        # and force=False pass a value for updatecheck. We may want to allow
        # updatecheck='abort' to better suppport some of these callers.
        if updatecheck is None:
            updatecheck = UPDATECHECK_LINEAR
        if updatecheck not in (
            UPDATECHECK_NONE,
            UPDATECHECK_LINEAR,
            UPDATECHECK_NO_CONFLICT,
        ):
            raise ValueError(
                r'Invalid updatecheck %r (can accept %r)'
                % (
                    updatecheck,
                    (
                        UPDATECHECK_NONE,
                        UPDATECHECK_LINEAR,
                        UPDATECHECK_NO_CONFLICT,
                    ),
                )
            )
    # If we're doing a partial update, we need to skip updating
    # the dirstate, so make a note of any partial-ness to the
    # update here.
    if matcher is None or matcher.always():
        partial = False
    else:
        partial = True
    with repo.wlock():
        if wc is None:
            wc = repo[None]
        pl = wc.parents()
        p1 = pl[0]
        p2 = repo[node]
        if ancestor is not None:
            pas = [repo[ancestor]]
        else:
            if repo.ui.configlist(b'merge', b'preferancestor') == [b'*']:
                cahs = repo.changelog.commonancestorsheads(p1.node(), p2.node())
                pas = [repo[anc] for anc in (sorted(cahs) or [nullid])]
            else:
                pas = [p1.ancestor(p2, warn=branchmerge)]

        fp1, fp2, xp1, xp2 = p1.node(), p2.node(), bytes(p1), bytes(p2)

        overwrite = force and not branchmerge
        ### check phase
        if not overwrite:
            if len(pl) > 1:
                raise error.Abort(_(b"outstanding uncommitted merge"))
            ms = mergestate.read(repo)
            if list(ms.unresolved()):
                raise error.Abort(
                    _(b"outstanding merge conflicts"),
                    hint=_(b"use 'hg resolve' to resolve"),
                )
        if branchmerge:
            if pas == [p2]:
                raise error.Abort(
                    _(
                        b"merging with a working directory ancestor"
                        b" has no effect"
                    )
                )
            elif pas == [p1]:
                if not mergeancestor and wc.branch() == p2.branch():
                    raise error.Abort(
                        _(b"nothing to merge"),
                        hint=_(b"use 'hg update' or check 'hg heads'"),
                    )
            if not force and (wc.files() or wc.deleted()):
                raise error.Abort(
                    _(b"uncommitted changes"),
                    hint=_(b"use 'hg status' to list changes"),
                )
            if not wc.isinmemory():
                for s in sorted(wc.substate):
                    wc.sub(s).bailifchanged()

        elif not overwrite:
            if p1 == p2:  # no-op update
                # call the hooks and exit early
                repo.hook(b'preupdate', throw=True, parent1=xp2, parent2=b'')
                repo.hook(b'update', parent1=xp2, parent2=b'', error=0)
                return updateresult(0, 0, 0, 0)

            if updatecheck == UPDATECHECK_LINEAR and pas not in (
                [p1],
                [p2],
            ):  # nonlinear
                dirty = wc.dirty(missing=True)
                if dirty:
                    # Branching is a bit strange to ensure we do the minimal
                    # amount of call to obsutil.foreground.
                    foreground = obsutil.foreground(repo, [p1.node()])
                    # note: the <node> variable contains a random identifier
                    if repo[node].node() in foreground:
                        pass  # allow updating to successors
                    else:
                        msg = _(b"uncommitted changes")
                        hint = _(b"commit or update --clean to discard changes")
                        raise error.UpdateAbort(msg, hint=hint)
                else:
                    # Allow jumping branches if clean and specific rev given
                    pass

        if overwrite:
            pas = [wc]
        elif not branchmerge:
            pas = [p1]

        # deprecated config: merge.followcopies
        followcopies = repo.ui.configbool(b'merge', b'followcopies')
        if overwrite:
            followcopies = False
        elif not pas[0]:
            followcopies = False
        if not branchmerge and not wc.dirty(missing=True):
            followcopies = False

        ### calculate phase
        actionbyfile, diverge, renamedelete = calculateupdates(
            repo,
            wc,
            p2,
            pas,
            branchmerge,
            force,
            mergeancestor,
            followcopies,
            matcher=matcher,
            mergeforce=mergeforce,
        )

        if updatecheck == UPDATECHECK_NO_CONFLICT:
            for f, (m, args, msg) in pycompat.iteritems(actionbyfile):
                if m not in (
                    ACTION_GET,
                    ACTION_KEEP,
                    ACTION_EXEC,
                    ACTION_REMOVE,
                    ACTION_PATH_CONFLICT_RESOLVE,
                ):
                    msg = _(b"conflicting changes")
                    hint = _(b"commit or update --clean to discard changes")
                    raise error.Abort(msg, hint=hint)

        # Prompt and create actions. Most of this is in the resolve phase
        # already, but we can't handle .hgsubstate in filemerge or
        # subrepoutil.submerge yet so we have to keep prompting for it.
        if b'.hgsubstate' in actionbyfile:
            f = b'.hgsubstate'
            m, args, msg = actionbyfile[f]
            prompts = filemerge.partextras(labels)
            prompts[b'f'] = f
            if m == ACTION_CHANGED_DELETED:
                if repo.ui.promptchoice(
                    _(
                        b"local%(l)s changed %(f)s which other%(o)s deleted\n"
                        b"use (c)hanged version or (d)elete?"
                        b"$$ &Changed $$ &Delete"
                    )
                    % prompts,
                    0,
                ):
                    actionbyfile[f] = (ACTION_REMOVE, None, b'prompt delete')
                elif f in p1:
                    actionbyfile[f] = (
                        ACTION_ADD_MODIFIED,
                        None,
                        b'prompt keep',
                    )
                else:
                    actionbyfile[f] = (ACTION_ADD, None, b'prompt keep')
            elif m == ACTION_DELETED_CHANGED:
                f1, f2, fa, move, anc = args
                flags = p2[f2].flags()
                if (
                    repo.ui.promptchoice(
                        _(
                            b"other%(o)s changed %(f)s which local%(l)s deleted\n"
                            b"use (c)hanged version or leave (d)eleted?"
                            b"$$ &Changed $$ &Deleted"
                        )
                        % prompts,
                        0,
                    )
                    == 0
                ):
                    actionbyfile[f] = (
                        ACTION_GET,
                        (flags, False),
                        b'prompt recreating',
                    )
                else:
                    del actionbyfile[f]

        # Convert to dictionary-of-lists format
        actions = emptyactions()
        for f, (m, args, msg) in pycompat.iteritems(actionbyfile):
            if m not in actions:
                actions[m] = []
            actions[m].append((f, args, msg))

        if not util.fscasesensitive(repo.path):
            # check collision between files only in p2 for clean update
            if not branchmerge and (
                force or not wc.dirty(missing=True, branch=False)
            ):
                _checkcollision(repo, p2.manifest(), None)
            else:
                _checkcollision(repo, wc.manifest(), actions)

        # divergent renames
        for f, fl in sorted(pycompat.iteritems(diverge)):
            repo.ui.warn(
                _(
                    b"note: possible conflict - %s was renamed "
                    b"multiple times to:\n"
                )
                % f
            )
            for nf in sorted(fl):
                repo.ui.warn(b" %s\n" % nf)

        # rename and delete
        for f, fl in sorted(pycompat.iteritems(renamedelete)):
            repo.ui.warn(
                _(
                    b"note: possible conflict - %s was deleted "
                    b"and renamed to:\n"
                )
                % f
            )
            for nf in sorted(fl):
                repo.ui.warn(b" %s\n" % nf)

        ### apply phase
        if not branchmerge:  # just jump to the new rev
            fp1, fp2, xp1, xp2 = fp2, nullid, xp2, b''
        if not partial and not wc.isinmemory():
            repo.hook(b'preupdate', throw=True, parent1=xp1, parent2=xp2)
            # note that we're in the middle of an update
            repo.vfs.write(b'updatestate', p2.hex())

        # Advertise fsmonitor when its presence could be useful.
        #
        # We only advertise when performing an update from an empty working
        # directory. This typically only occurs during initial clone.
        #
        # We give users a mechanism to disable the warning in case it is
        # annoying.
        #
        # We only allow on Linux and MacOS because that's where fsmonitor is
        # considered stable.
        fsmonitorwarning = repo.ui.configbool(b'fsmonitor', b'warn_when_unused')
        fsmonitorthreshold = repo.ui.configint(
            b'fsmonitor', b'warn_update_file_count'
        )
        try:
            # avoid cycle: extensions -> cmdutil -> merge
            from . import extensions

            extensions.find(b'fsmonitor')
            fsmonitorenabled = repo.ui.config(b'fsmonitor', b'mode') != b'off'
            # We intentionally don't look at whether fsmonitor has disabled
            # itself because a) fsmonitor may have already printed a warning
            # b) we only care about the config state here.
        except KeyError:
            fsmonitorenabled = False

        if (
            fsmonitorwarning
            and not fsmonitorenabled
            and p1.node() == nullid
            and len(actions[ACTION_GET]) >= fsmonitorthreshold
            and pycompat.sysplatform.startswith((b'linux', b'darwin'))
        ):
            repo.ui.warn(
                _(
                    b'(warning: large working directory being used without '
                    b'fsmonitor enabled; enable fsmonitor to improve performance; '
                    b'see "hg help -e fsmonitor")\n'
                )
            )

        updatedirstate = not partial and not wc.isinmemory()
        wantfiledata = updatedirstate and not branchmerge
        stats, getfiledata = applyupdates(
            repo, actions, wc, p2, overwrite, wantfiledata, labels=labels
        )

        if updatedirstate:
            with repo.dirstate.parentchange():
                repo.setparents(fp1, fp2)
                recordupdates(repo, actions, branchmerge, getfiledata)
                # update completed, clear state
                util.unlink(repo.vfs.join(b'updatestate'))

                if not branchmerge:
                    repo.dirstate.setbranch(p2.branch())

    # If we're updating to a location, clean up any stale temporary includes
    # (ex: this happens during hg rebase --abort).
    if not branchmerge:
        sparse.prunetemporaryincludes(repo)

    if not partial:
        repo.hook(
            b'update', parent1=xp1, parent2=xp2, error=stats.unresolvedcount
        )
    return stats


def graft(
    repo, ctx, base, labels=None, keepparent=False, keepconflictparent=False
):
    """Do a graft-like merge.

    This is a merge where the merge ancestor is chosen such that one
    or more changesets are grafted onto the current changeset. In
    addition to the merge, this fixes up the dirstate to include only
    a single parent (if keepparent is False) and tries to duplicate any
    renames/copies appropriately.

    ctx - changeset to rebase
    base - merge base, usually ctx.p1()
    labels - merge labels eg ['local', 'graft']
    keepparent - keep second parent if any
    keepconflictparent - if unresolved, keep parent used for the merge

    """
    # If we're grafting a descendant onto an ancestor, be sure to pass
    # mergeancestor=True to update. This does two things: 1) allows the merge if
    # the destination is the same as the parent of the ctx (so we can use graft
    # to copy commits), and 2) informs update that the incoming changes are
    # newer than the destination so it doesn't prompt about "remote changed foo
    # which local deleted".
    wctx = repo[None]
    pctx = wctx.p1()
    mergeancestor = repo.changelog.isancestor(pctx.node(), ctx.node())

    stats = update(
        repo,
        ctx.node(),
        True,
        True,
        base.node(),
        mergeancestor=mergeancestor,
        labels=labels,
    )

    if keepconflictparent and stats.unresolvedcount:
        pother = ctx.node()
    else:
        pother = nullid
        parents = ctx.parents()
        if keepparent and len(parents) == 2 and base in parents:
            parents.remove(base)
            pother = parents[0].node()
    # Never set both parents equal to each other
    if pother == pctx.node():
        pother = nullid

    with repo.dirstate.parentchange():
        repo.setparents(pctx.node(), pother)
        repo.dirstate.write(repo.currenttransaction())
        # fix up dirstate for copies and renames
        copies.graftcopies(wctx, ctx, base)
    return stats


def purge(
    repo,
    matcher,
    ignored=False,
    removeemptydirs=True,
    removefiles=True,
    abortonerror=False,
    noop=False,
):
    """Purge the working directory of untracked files.

    ``matcher`` is a matcher configured to scan the working directory -
    potentially a subset.

    ``ignored`` controls whether ignored files should also be purged.

    ``removeemptydirs`` controls whether empty directories should be removed.

    ``removefiles`` controls whether files are removed.

    ``abortonerror`` causes an exception to be raised if an error occurs
    deleting a file or directory.

    ``noop`` controls whether to actually remove files. If not defined, actions
    will be taken.

    Returns an iterable of relative paths in the working directory that were
    or would be removed.
    """

    def remove(removefn, path):
        try:
            removefn(path)
        except OSError:
            m = _(b'%s cannot be removed') % path
            if abortonerror:
                raise error.Abort(m)
            else:
                repo.ui.warn(_(b'warning: %s\n') % m)

    # There's no API to copy a matcher. So mutate the passed matcher and
    # restore it when we're done.
    oldtraversedir = matcher.traversedir

    res = []

    try:
        if removeemptydirs:
            directories = []
            matcher.traversedir = directories.append

        status = repo.status(match=matcher, ignored=ignored, unknown=True)

        if removefiles:
            for f in sorted(status.unknown + status.ignored):
                if not noop:
                    repo.ui.note(_(b'removing file %s\n') % f)
                    remove(repo.wvfs.unlink, f)
                res.append(f)

        if removeemptydirs:
            for f in sorted(directories, reverse=True):
                if matcher(f) and not repo.wvfs.listdir(f):
                    if not noop:
                        repo.ui.note(_(b'removing directory %s\n') % f)
                        remove(repo.wvfs.rmdir, f)
                    res.append(f)

        return res

    finally:
        matcher.traversedir = oldtraversedir
