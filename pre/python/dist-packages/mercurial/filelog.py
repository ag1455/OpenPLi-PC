# filelog.py - file history class for mercurial
#
# Copyright 2005-2007 Matt Mackall <mpm@selenic.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

from .i18n import _
from .node import (
    nullid,
    nullrev,
)
from . import (
    error,
    revlog,
)
from .interfaces import (
    repository,
    util as interfaceutil,
)
from .utils import storageutil


@interfaceutil.implementer(repository.ifilestorage)
class filelog(object):
    def __init__(self, opener, path):
        self._revlog = revlog.revlog(
            opener, b'/'.join((b'data', path + b'.i')), censorable=True
        )
        # Full name of the user visible file, relative to the repository root.
        # Used by LFS.
        self._revlog.filename = path

    def __len__(self):
        return len(self._revlog)

    def __iter__(self):
        return self._revlog.__iter__()

    def hasnode(self, node):
        if node in (nullid, nullrev):
            return False

        try:
            self._revlog.rev(node)
            return True
        except (TypeError, ValueError, IndexError, error.LookupError):
            return False

    def revs(self, start=0, stop=None):
        return self._revlog.revs(start=start, stop=stop)

    def parents(self, node):
        return self._revlog.parents(node)

    def parentrevs(self, rev):
        return self._revlog.parentrevs(rev)

    def rev(self, node):
        return self._revlog.rev(node)

    def node(self, rev):
        return self._revlog.node(rev)

    def lookup(self, node):
        return storageutil.fileidlookup(
            self._revlog, node, self._revlog.indexfile
        )

    def linkrev(self, rev):
        return self._revlog.linkrev(rev)

    def commonancestorsheads(self, node1, node2):
        return self._revlog.commonancestorsheads(node1, node2)

    # Used by dagop.blockdescendants().
    def descendants(self, revs):
        return self._revlog.descendants(revs)

    def heads(self, start=None, stop=None):
        return self._revlog.heads(start, stop)

    # Used by hgweb, children extension.
    def children(self, node):
        return self._revlog.children(node)

    def iscensored(self, rev):
        return self._revlog.iscensored(rev)

    def revision(self, node, _df=None, raw=False):
        return self._revlog.revision(node, _df=_df, raw=raw)

    def rawdata(self, node, _df=None):
        return self._revlog.rawdata(node, _df=_df)

    def emitrevisions(
        self,
        nodes,
        nodesorder=None,
        revisiondata=False,
        assumehaveparentrevisions=False,
        deltamode=repository.CG_DELTAMODE_STD,
    ):
        return self._revlog.emitrevisions(
            nodes,
            nodesorder=nodesorder,
            revisiondata=revisiondata,
            assumehaveparentrevisions=assumehaveparentrevisions,
            deltamode=deltamode,
        )

    def addrevision(
        self,
        revisiondata,
        transaction,
        linkrev,
        p1,
        p2,
        node=None,
        flags=revlog.REVIDX_DEFAULT_FLAGS,
        cachedelta=None,
    ):
        return self._revlog.addrevision(
            revisiondata,
            transaction,
            linkrev,
            p1,
            p2,
            node=node,
            flags=flags,
            cachedelta=cachedelta,
        )

    def addgroup(
        self,
        deltas,
        linkmapper,
        transaction,
        addrevisioncb=None,
        maybemissingparents=False,
    ):
        if maybemissingparents:
            raise error.Abort(
                _(
                    b'revlog storage does not support missing '
                    b'parents write mode'
                )
            )

        return self._revlog.addgroup(
            deltas, linkmapper, transaction, addrevisioncb=addrevisioncb
        )

    def getstrippoint(self, minlink):
        return self._revlog.getstrippoint(minlink)

    def strip(self, minlink, transaction):
        return self._revlog.strip(minlink, transaction)

    def censorrevision(self, tr, node, tombstone=b''):
        return self._revlog.censorrevision(tr, node, tombstone=tombstone)

    def files(self):
        return self._revlog.files()

    def read(self, node):
        return storageutil.filtermetadata(self.revision(node))

    def add(self, text, meta, transaction, link, p1=None, p2=None):
        if meta or text.startswith(b'\1\n'):
            text = storageutil.packmeta(meta, text)
        return self.addrevision(text, transaction, link, p1, p2)

    def renamed(self, node):
        return storageutil.filerevisioncopied(self, node)

    def size(self, rev):
        """return the size of a given revision"""

        # for revisions with renames, we have to go the slow way
        node = self.node(rev)
        if self.renamed(node):
            return len(self.read(node))
        if self.iscensored(rev):
            return 0

        # XXX if self.read(node).startswith("\1\n"), this returns (size+4)
        return self._revlog.size(rev)

    def cmp(self, node, text):
        """compare text with a given file revision

        returns True if text is different than what is stored.
        """
        return not storageutil.filedataequivalent(self, node, text)

    def verifyintegrity(self, state):
        return self._revlog.verifyintegrity(state)

    def storageinfo(
        self,
        exclusivefiles=False,
        sharedfiles=False,
        revisionscount=False,
        trackedsize=False,
        storedsize=False,
    ):
        return self._revlog.storageinfo(
            exclusivefiles=exclusivefiles,
            sharedfiles=sharedfiles,
            revisionscount=revisionscount,
            trackedsize=trackedsize,
            storedsize=storedsize,
        )

    # TODO these aren't part of the interface and aren't internal methods.
    # Callers should be fixed to not use them.

    # Used by bundlefilelog, unionfilelog.
    @property
    def indexfile(self):
        return self._revlog.indexfile

    @indexfile.setter
    def indexfile(self, value):
        self._revlog.indexfile = value

    # Used by repo upgrade.
    def clone(self, tr, destrevlog, **kwargs):
        if not isinstance(destrevlog, filelog):
            raise error.ProgrammingError(b'expected filelog to clone()')

        return self._revlog.clone(tr, destrevlog._revlog, **kwargs)


class narrowfilelog(filelog):
    """Filelog variation to be used with narrow stores."""

    def __init__(self, opener, path, narrowmatch):
        super(narrowfilelog, self).__init__(opener, path)
        self._narrowmatch = narrowmatch

    def renamed(self, node):
        res = super(narrowfilelog, self).renamed(node)

        # Renames that come from outside the narrowspec are problematic
        # because we may lack the base text for the rename. This can result
        # in code attempting to walk the ancestry or compute a diff
        # encountering a missing revision. We address this by silently
        # removing rename metadata if the source file is outside the
        # narrow spec.
        #
        # A better solution would be to see if the base revision is available,
        # rather than assuming it isn't.
        #
        # An even better solution would be to teach all consumers of rename
        # metadata that the base revision may not be available.
        #
        # TODO consider better ways of doing this.
        if res and not self._narrowmatch(res[0]):
            return None

        return res

    def size(self, rev):
        # Because we have a custom renamed() that may lie, we need to call
        # the base renamed() to report accurate results.
        node = self.node(rev)
        if super(narrowfilelog, self).renamed(node):
            return len(self.read(node))
        else:
            return super(narrowfilelog, self).size(rev)

    def cmp(self, node, text):
        different = super(narrowfilelog, self).cmp(node, text)

        # Because renamed() may lie, we may get false positives for
        # different content. Check for this by comparing against the original
        # renamed() implementation.
        if different:
            if super(narrowfilelog, self).renamed(node):
                t2 = self.read(node)
                return t2 != text

        return different
