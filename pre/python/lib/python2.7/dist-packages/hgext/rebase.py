# rebase.py - rebasing feature for mercurial
#
# Copyright 2008 Stefano Tortarolo <stefano.tortarolo at gmail dot com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

'''command to move sets of revisions to a different ancestor

This extension lets you rebase changesets in an existing Mercurial
repository.

For more information:
https://mercurial-scm.org/wiki/RebaseExtension
'''

from __future__ import absolute_import

import errno
import os

from mercurial.i18n import _
from mercurial.node import (
    nullrev,
    short,
)
from mercurial.pycompat import open
from mercurial import (
    bookmarks,
    cmdutil,
    commands,
    copies,
    destutil,
    dirstateguard,
    error,
    extensions,
    hg,
    merge as mergemod,
    mergeutil,
    obsolete,
    obsutil,
    patch,
    phases,
    pycompat,
    registrar,
    repair,
    revset,
    revsetlang,
    rewriteutil,
    scmutil,
    smartset,
    state as statemod,
    util,
)

# The following constants are used throughout the rebase module. The ordering of
# their values must be maintained.

# Indicates that a revision needs to be rebased
revtodo = -1
revtodostr = b'-1'

# legacy revstates no longer needed in current code
# -2: nullmerge, -3: revignored, -4: revprecursor, -5: revpruned
legacystates = {b'-2', b'-3', b'-4', b'-5'}

cmdtable = {}
command = registrar.command(cmdtable)
# Note for extension authors: ONLY specify testedwith = 'ships-with-hg-core' for
# extensions which SHIP WITH MERCURIAL. Non-mainline extensions should
# be specifying the version(s) of Mercurial they are tested with, or
# leave the attribute unspecified.
testedwith = b'ships-with-hg-core'


def _nothingtorebase():
    return 1


def _savegraft(ctx, extra):
    s = ctx.extra().get(b'source', None)
    if s is not None:
        extra[b'source'] = s
    s = ctx.extra().get(b'intermediate-source', None)
    if s is not None:
        extra[b'intermediate-source'] = s


def _savebranch(ctx, extra):
    extra[b'branch'] = ctx.branch()


def _destrebase(repo, sourceset, destspace=None):
    """small wrapper around destmerge to pass the right extra args

    Please wrap destutil.destmerge instead."""
    return destutil.destmerge(
        repo,
        action=b'rebase',
        sourceset=sourceset,
        onheadcheck=False,
        destspace=destspace,
    )


revsetpredicate = registrar.revsetpredicate()


@revsetpredicate(b'_destrebase')
def _revsetdestrebase(repo, subset, x):
    # ``_rebasedefaultdest()``

    # default destination for rebase.
    # # XXX: Currently private because I expect the signature to change.
    # # XXX: - bailing out in case of ambiguity vs returning all data.
    # i18n: "_rebasedefaultdest" is a keyword
    sourceset = None
    if x is not None:
        sourceset = revset.getset(repo, smartset.fullreposet(repo), x)
    return subset & smartset.baseset([_destrebase(repo, sourceset)])


@revsetpredicate(b'_destautoorphanrebase')
def _revsetdestautoorphanrebase(repo, subset, x):
    # ``_destautoorphanrebase()``

    # automatic rebase destination for a single orphan revision.
    unfi = repo.unfiltered()
    obsoleted = unfi.revs(b'obsolete()')

    src = revset.getset(repo, subset, x).first()

    # Empty src or already obsoleted - Do not return a destination
    if not src or src in obsoleted:
        return smartset.baseset()
    dests = destutil.orphanpossibledestination(repo, src)
    if len(dests) > 1:
        raise error.Abort(
            _(b"ambiguous automatic rebase: %r could end up on any of %r")
            % (src, dests)
        )
    # We have zero or one destination, so we can just return here.
    return smartset.baseset(dests)


def _ctxdesc(ctx):
    """short description for a context"""
    desc = b'%d:%s "%s"' % (
        ctx.rev(),
        ctx,
        ctx.description().split(b'\n', 1)[0],
    )
    repo = ctx.repo()
    names = []
    for nsname, ns in pycompat.iteritems(repo.names):
        if nsname == b'branches':
            continue
        names.extend(ns.names(repo, ctx.node()))
    if names:
        desc += b' (%s)' % b' '.join(names)
    return desc


class rebaseruntime(object):
    """This class is a container for rebase runtime state"""

    def __init__(self, repo, ui, inmemory=False, opts=None):
        if opts is None:
            opts = {}

        # prepared: whether we have rebasestate prepared or not. Currently it
        # decides whether "self.repo" is unfiltered or not.
        # The rebasestate has explicit hash to hash instructions not depending
        # on visibility. If rebasestate exists (in-memory or on-disk), use
        # unfiltered repo to avoid visibility issues.
        # Before knowing rebasestate (i.e. when starting a new rebase (not
        # --continue or --abort)), the original repo should be used so
        # visibility-dependent revsets are correct.
        self.prepared = False
        self._repo = repo

        self.ui = ui
        self.opts = opts
        self.originalwd = None
        self.external = nullrev
        # Mapping between the old revision id and either what is the new rebased
        # revision or what needs to be done with the old revision. The state
        # dict will be what contains most of the rebase progress state.
        self.state = {}
        self.activebookmark = None
        self.destmap = {}
        self.skipped = set()

        self.collapsef = opts.get(b'collapse', False)
        self.collapsemsg = cmdutil.logmessage(ui, opts)
        self.date = opts.get(b'date', None)

        e = opts.get(b'extrafn')  # internal, used by e.g. hgsubversion
        self.extrafns = [_savegraft]
        if e:
            self.extrafns = [e]

        self.backupf = ui.configbool(b'rewrite', b'backup-bundle')
        self.keepf = opts.get(b'keep', False)
        self.keepbranchesf = opts.get(b'keepbranches', False)
        self.obsoletenotrebased = {}
        self.obsoletewithoutsuccessorindestination = set()
        self.inmemory = inmemory
        self.stateobj = statemod.cmdstate(repo, b'rebasestate')

    @property
    def repo(self):
        if self.prepared:
            return self._repo.unfiltered()
        else:
            return self._repo

    def storestatus(self, tr=None):
        """Store the current status to allow recovery"""
        if tr:
            tr.addfilegenerator(
                b'rebasestate',
                (b'rebasestate',),
                self._writestatus,
                location=b'plain',
            )
        else:
            with self.repo.vfs(b"rebasestate", b"w") as f:
                self._writestatus(f)

    def _writestatus(self, f):
        repo = self.repo
        assert repo.filtername is None
        f.write(repo[self.originalwd].hex() + b'\n')
        # was "dest". we now write dest per src root below.
        f.write(b'\n')
        f.write(repo[self.external].hex() + b'\n')
        f.write(b'%d\n' % int(self.collapsef))
        f.write(b'%d\n' % int(self.keepf))
        f.write(b'%d\n' % int(self.keepbranchesf))
        f.write(b'%s\n' % (self.activebookmark or b''))
        destmap = self.destmap
        for d, v in pycompat.iteritems(self.state):
            oldrev = repo[d].hex()
            if v >= 0:
                newrev = repo[v].hex()
            else:
                newrev = b"%d" % v
            destnode = repo[destmap[d]].hex()
            f.write(b"%s:%s:%s\n" % (oldrev, newrev, destnode))
        repo.ui.debug(b'rebase status stored\n')

    def restorestatus(self):
        """Restore a previously stored status"""
        if not self.stateobj.exists():
            cmdutil.wrongtooltocontinue(self.repo, _(b'rebase'))

        data = self._read()
        self.repo.ui.debug(b'rebase status resumed\n')

        self.originalwd = data[b'originalwd']
        self.destmap = data[b'destmap']
        self.state = data[b'state']
        self.skipped = data[b'skipped']
        self.collapsef = data[b'collapse']
        self.keepf = data[b'keep']
        self.keepbranchesf = data[b'keepbranches']
        self.external = data[b'external']
        self.activebookmark = data[b'activebookmark']

    def _read(self):
        self.prepared = True
        repo = self.repo
        assert repo.filtername is None
        data = {
            b'keepbranches': None,
            b'collapse': None,
            b'activebookmark': None,
            b'external': nullrev,
            b'keep': None,
            b'originalwd': None,
        }
        legacydest = None
        state = {}
        destmap = {}

        if True:
            f = repo.vfs(b"rebasestate")
            for i, l in enumerate(f.read().splitlines()):
                if i == 0:
                    data[b'originalwd'] = repo[l].rev()
                elif i == 1:
                    # this line should be empty in newer version. but legacy
                    # clients may still use it
                    if l:
                        legacydest = repo[l].rev()
                elif i == 2:
                    data[b'external'] = repo[l].rev()
                elif i == 3:
                    data[b'collapse'] = bool(int(l))
                elif i == 4:
                    data[b'keep'] = bool(int(l))
                elif i == 5:
                    data[b'keepbranches'] = bool(int(l))
                elif i == 6 and not (len(l) == 81 and b':' in l):
                    # line 6 is a recent addition, so for backwards
                    # compatibility check that the line doesn't look like the
                    # oldrev:newrev lines
                    data[b'activebookmark'] = l
                else:
                    args = l.split(b':')
                    oldrev = repo[args[0]].rev()
                    newrev = args[1]
                    if newrev in legacystates:
                        continue
                    if len(args) > 2:
                        destrev = repo[args[2]].rev()
                    else:
                        destrev = legacydest
                    destmap[oldrev] = destrev
                    if newrev == revtodostr:
                        state[oldrev] = revtodo
                        # Legacy compat special case
                    else:
                        state[oldrev] = repo[newrev].rev()

        if data[b'keepbranches'] is None:
            raise error.Abort(_(b'.hg/rebasestate is incomplete'))

        data[b'destmap'] = destmap
        data[b'state'] = state
        skipped = set()
        # recompute the set of skipped revs
        if not data[b'collapse']:
            seen = set(destmap.values())
            for old, new in sorted(state.items()):
                if new != revtodo and new in seen:
                    skipped.add(old)
                seen.add(new)
        data[b'skipped'] = skipped
        repo.ui.debug(
            b'computed skipped revs: %s\n'
            % (b' '.join(b'%d' % r for r in sorted(skipped)) or b'')
        )

        return data

    def _handleskippingobsolete(self, obsoleterevs, destmap):
        """Compute structures necessary for skipping obsolete revisions

        obsoleterevs:   iterable of all obsolete revisions in rebaseset
        destmap:        {srcrev: destrev} destination revisions
        """
        self.obsoletenotrebased = {}
        if not self.ui.configbool(b'experimental', b'rebaseskipobsolete'):
            return
        obsoleteset = set(obsoleterevs)
        (
            self.obsoletenotrebased,
            self.obsoletewithoutsuccessorindestination,
            obsoleteextinctsuccessors,
        ) = _computeobsoletenotrebased(self.repo, obsoleteset, destmap)
        skippedset = set(self.obsoletenotrebased)
        skippedset.update(self.obsoletewithoutsuccessorindestination)
        skippedset.update(obsoleteextinctsuccessors)
        _checkobsrebase(self.repo, self.ui, obsoleteset, skippedset)

    def _prepareabortorcontinue(self, isabort, backup=True, suppwarns=False):
        try:
            self.restorestatus()
            self.collapsemsg = restorecollapsemsg(self.repo, isabort)
        except error.RepoLookupError:
            if isabort:
                clearstatus(self.repo)
                clearcollapsemsg(self.repo)
                self.repo.ui.warn(
                    _(
                        b'rebase aborted (no revision is removed,'
                        b' only broken state is cleared)\n'
                    )
                )
                return 0
            else:
                msg = _(b'cannot continue inconsistent rebase')
                hint = _(b'use "hg rebase --abort" to clear broken state')
                raise error.Abort(msg, hint=hint)

        if isabort:
            backup = backup and self.backupf
            return self._abort(backup=backup, suppwarns=suppwarns)

    def _preparenewrebase(self, destmap):
        if not destmap:
            return _nothingtorebase()

        rebaseset = destmap.keys()
        if not self.keepf:
            try:
                rewriteutil.precheck(self.repo, rebaseset, action=b'rebase')
            except error.Abort as e:
                if e.hint is None:
                    e.hint = _(b'use --keep to keep original changesets')
                raise e

        result = buildstate(self.repo, destmap, self.collapsef)

        if not result:
            # Empty state built, nothing to rebase
            self.ui.status(_(b'nothing to rebase\n'))
            return _nothingtorebase()

        (self.originalwd, self.destmap, self.state) = result
        if self.collapsef:
            dests = set(self.destmap.values())
            if len(dests) != 1:
                raise error.Abort(
                    _(b'--collapse does not work with multiple destinations')
                )
            destrev = next(iter(dests))
            destancestors = self.repo.changelog.ancestors(
                [destrev], inclusive=True
            )
            self.external = externalparent(self.repo, self.state, destancestors)

        for destrev in sorted(set(destmap.values())):
            dest = self.repo[destrev]
            if dest.closesbranch() and not self.keepbranchesf:
                self.ui.status(_(b'reopening closed branch head %s\n') % dest)

        self.prepared = True

    def _assignworkingcopy(self):
        if self.inmemory:
            from mercurial.context import overlayworkingctx

            self.wctx = overlayworkingctx(self.repo)
            self.repo.ui.debug(b"rebasing in-memory\n")
        else:
            self.wctx = self.repo[None]
            self.repo.ui.debug(b"rebasing on disk\n")
        self.repo.ui.log(
            b"rebase",
            b"using in-memory rebase: %r\n",
            self.inmemory,
            rebase_imm_used=self.inmemory,
        )

    def _performrebase(self, tr):
        self._assignworkingcopy()
        repo, ui = self.repo, self.ui
        if self.keepbranchesf:
            # insert _savebranch at the start of extrafns so if
            # there's a user-provided extrafn it can clobber branch if
            # desired
            self.extrafns.insert(0, _savebranch)
            if self.collapsef:
                branches = set()
                for rev in self.state:
                    branches.add(repo[rev].branch())
                    if len(branches) > 1:
                        raise error.Abort(
                            _(b'cannot collapse multiple named branches')
                        )

        # Calculate self.obsoletenotrebased
        obsrevs = _filterobsoleterevs(self.repo, self.state)
        self._handleskippingobsolete(obsrevs, self.destmap)

        # Keep track of the active bookmarks in order to reset them later
        self.activebookmark = self.activebookmark or repo._activebookmark
        if self.activebookmark:
            bookmarks.deactivate(repo)

        # Store the state before we begin so users can run 'hg rebase --abort'
        # if we fail before the transaction closes.
        self.storestatus()
        if tr:
            # When using single transaction, store state when transaction
            # commits.
            self.storestatus(tr)

        cands = [k for k, v in pycompat.iteritems(self.state) if v == revtodo]
        p = repo.ui.makeprogress(
            _(b"rebasing"), unit=_(b'changesets'), total=len(cands)
        )

        def progress(ctx):
            p.increment(item=(b"%d:%s" % (ctx.rev(), ctx)))

        allowdivergence = self.ui.configbool(
            b'experimental', b'evolution.allowdivergence'
        )
        for subset in sortsource(self.destmap):
            sortedrevs = self.repo.revs(b'sort(%ld, -topo)', subset)
            if not allowdivergence:
                sortedrevs -= self.repo.revs(
                    b'descendants(%ld) and not %ld',
                    self.obsoletewithoutsuccessorindestination,
                    self.obsoletewithoutsuccessorindestination,
                )
            for rev in sortedrevs:
                self._rebasenode(tr, rev, allowdivergence, progress)
        p.complete()
        ui.note(_(b'rebase merging completed\n'))

    def _concludenode(self, rev, p1, p2, editor, commitmsg=None):
        '''Commit the wd changes with parents p1 and p2.

        Reuse commit info from rev but also store useful information in extra.
        Return node of committed revision.'''
        repo = self.repo
        ctx = repo[rev]
        if commitmsg is None:
            commitmsg = ctx.description()
        date = self.date
        if date is None:
            date = ctx.date()
        extra = {b'rebase_source': ctx.hex()}
        for c in self.extrafns:
            c(ctx, extra)
        keepbranch = self.keepbranchesf and repo[p1].branch() != ctx.branch()
        destphase = max(ctx.phase(), phases.draft)
        overrides = {(b'phases', b'new-commit'): destphase}
        if keepbranch:
            overrides[(b'ui', b'allowemptycommit')] = True
        with repo.ui.configoverride(overrides, b'rebase'):
            if self.inmemory:
                newnode = commitmemorynode(
                    repo,
                    p1,
                    p2,
                    wctx=self.wctx,
                    extra=extra,
                    commitmsg=commitmsg,
                    editor=editor,
                    user=ctx.user(),
                    date=date,
                )
                mergemod.mergestate.clean(repo)
            else:
                newnode = commitnode(
                    repo,
                    p1,
                    p2,
                    extra=extra,
                    commitmsg=commitmsg,
                    editor=editor,
                    user=ctx.user(),
                    date=date,
                )

            if newnode is None:
                # If it ended up being a no-op commit, then the normal
                # merge state clean-up path doesn't happen, so do it
                # here. Fix issue5494
                mergemod.mergestate.clean(repo)
            return newnode

    def _rebasenode(self, tr, rev, allowdivergence, progressfn):
        repo, ui, opts = self.repo, self.ui, self.opts
        dest = self.destmap[rev]
        ctx = repo[rev]
        desc = _ctxdesc(ctx)
        if self.state[rev] == rev:
            ui.status(_(b'already rebased %s\n') % desc)
        elif (
            not allowdivergence
            and rev in self.obsoletewithoutsuccessorindestination
        ):
            msg = (
                _(
                    b'note: not rebasing %s and its descendants as '
                    b'this would cause divergence\n'
                )
                % desc
            )
            repo.ui.status(msg)
            self.skipped.add(rev)
        elif rev in self.obsoletenotrebased:
            succ = self.obsoletenotrebased[rev]
            if succ is None:
                msg = _(b'note: not rebasing %s, it has no successor\n') % desc
            else:
                succdesc = _ctxdesc(repo[succ])
                msg = _(
                    b'note: not rebasing %s, already in destination as %s\n'
                ) % (desc, succdesc)
            repo.ui.status(msg)
            # Make clearrebased aware state[rev] is not a true successor
            self.skipped.add(rev)
            # Record rev as moved to its desired destination in self.state.
            # This helps bookmark and working parent movement.
            dest = max(
                adjustdest(repo, rev, self.destmap, self.state, self.skipped)
            )
            self.state[rev] = dest
        elif self.state[rev] == revtodo:
            ui.status(_(b'rebasing %s\n') % desc)
            progressfn(ctx)
            p1, p2, base = defineparents(
                repo,
                rev,
                self.destmap,
                self.state,
                self.skipped,
                self.obsoletenotrebased,
            )
            if not self.inmemory and len(repo[None].parents()) == 2:
                repo.ui.debug(b'resuming interrupted rebase\n')
            else:
                overrides = {(b'ui', b'forcemerge'): opts.get(b'tool', b'')}
                with ui.configoverride(overrides, b'rebase'):
                    stats = rebasenode(
                        repo,
                        rev,
                        p1,
                        base,
                        self.collapsef,
                        dest,
                        wctx=self.wctx,
                    )
                    if stats.unresolvedcount > 0:
                        if self.inmemory:
                            raise error.InMemoryMergeConflictsError()
                        else:
                            raise error.InterventionRequired(
                                _(
                                    b'unresolved conflicts (see hg '
                                    b'resolve, then hg rebase --continue)'
                                )
                            )
            if not self.collapsef:
                merging = p2 != nullrev
                editform = cmdutil.mergeeditform(merging, b'rebase')
                editor = cmdutil.getcommiteditor(
                    editform=editform, **pycompat.strkwargs(opts)
                )
                newnode = self._concludenode(rev, p1, p2, editor)
            else:
                # Skip commit if we are collapsing
                if self.inmemory:
                    self.wctx.setbase(repo[p1])
                else:
                    repo.setparents(repo[p1].node())
                newnode = None
            # Update the state
            if newnode is not None:
                self.state[rev] = repo[newnode].rev()
                ui.debug(b'rebased as %s\n' % short(newnode))
            else:
                if not self.collapsef:
                    ui.warn(
                        _(
                            b'note: not rebasing %s, its destination already '
                            b'has all its changes\n'
                        )
                        % desc
                    )
                    self.skipped.add(rev)
                self.state[rev] = p1
                ui.debug(b'next revision set to %d\n' % p1)
        else:
            ui.status(
                _(b'already rebased %s as %s\n') % (desc, repo[self.state[rev]])
            )
        if not tr:
            # When not using single transaction, store state after each
            # commit is completely done. On InterventionRequired, we thus
            # won't store the status. Instead, we'll hit the "len(parents) == 2"
            # case and realize that the commit was in progress.
            self.storestatus()

    def _finishrebase(self):
        repo, ui, opts = self.repo, self.ui, self.opts
        fm = ui.formatter(b'rebase', opts)
        fm.startitem()
        if self.collapsef:
            p1, p2, _base = defineparents(
                repo,
                min(self.state),
                self.destmap,
                self.state,
                self.skipped,
                self.obsoletenotrebased,
            )
            editopt = opts.get(b'edit')
            editform = b'rebase.collapse'
            if self.collapsemsg:
                commitmsg = self.collapsemsg
            else:
                commitmsg = b'Collapsed revision'
                for rebased in sorted(self.state):
                    if rebased not in self.skipped:
                        commitmsg += b'\n* %s' % repo[rebased].description()
                editopt = True
            editor = cmdutil.getcommiteditor(edit=editopt, editform=editform)
            revtoreuse = max(self.state)

            newnode = self._concludenode(
                revtoreuse, p1, self.external, editor, commitmsg=commitmsg
            )

            if newnode is not None:
                newrev = repo[newnode].rev()
                for oldrev in self.state:
                    self.state[oldrev] = newrev

        if b'qtip' in repo.tags():
            updatemq(repo, self.state, self.skipped, **pycompat.strkwargs(opts))

        # restore original working directory
        # (we do this before stripping)
        newwd = self.state.get(self.originalwd, self.originalwd)
        if newwd < 0:
            # original directory is a parent of rebase set root or ignored
            newwd = self.originalwd
        if newwd not in [c.rev() for c in repo[None].parents()]:
            ui.note(_(b"update back to initial working directory parent\n"))
            hg.updaterepo(repo, newwd, overwrite=False)

        collapsedas = None
        if self.collapsef and not self.keepf:
            collapsedas = newnode
        clearrebased(
            ui,
            repo,
            self.destmap,
            self.state,
            self.skipped,
            collapsedas,
            self.keepf,
            fm=fm,
            backup=self.backupf,
        )

        clearstatus(repo)
        clearcollapsemsg(repo)

        ui.note(_(b"rebase completed\n"))
        util.unlinkpath(repo.sjoin(b'undo'), ignoremissing=True)
        if self.skipped:
            skippedlen = len(self.skipped)
            ui.note(_(b"%d revisions have been skipped\n") % skippedlen)
        fm.end()

        if (
            self.activebookmark
            and self.activebookmark in repo._bookmarks
            and repo[b'.'].node() == repo._bookmarks[self.activebookmark]
        ):
            bookmarks.activate(repo, self.activebookmark)

    def _abort(self, backup=True, suppwarns=False):
        '''Restore the repository to its original state.'''

        repo = self.repo
        try:
            # If the first commits in the rebased set get skipped during the
            # rebase, their values within the state mapping will be the dest
            # rev id. The rebased list must must not contain the dest rev
            # (issue4896)
            rebased = [
                s
                for r, s in self.state.items()
                if s >= 0 and s != r and s != self.destmap[r]
            ]
            immutable = [d for d in rebased if not repo[d].mutable()]
            cleanup = True
            if immutable:
                repo.ui.warn(
                    _(b"warning: can't clean up public changesets %s\n")
                    % b', '.join(bytes(repo[r]) for r in immutable),
                    hint=_(b"see 'hg help phases' for details"),
                )
                cleanup = False

            descendants = set()
            if rebased:
                descendants = set(repo.changelog.descendants(rebased))
            if descendants - set(rebased):
                repo.ui.warn(
                    _(
                        b"warning: new changesets detected on "
                        b"destination branch, can't strip\n"
                    )
                )
                cleanup = False

            if cleanup:
                if rebased:
                    strippoints = [
                        c.node() for c in repo.set(b'roots(%ld)', rebased)
                    ]

                updateifonnodes = set(rebased)
                updateifonnodes.update(self.destmap.values())
                updateifonnodes.add(self.originalwd)
                shouldupdate = repo[b'.'].rev() in updateifonnodes

                # Update away from the rebase if necessary
                if shouldupdate:
                    mergemod.update(
                        repo, self.originalwd, branchmerge=False, force=True
                    )

                # Strip from the first rebased revision
                if rebased:
                    repair.strip(repo.ui, repo, strippoints, backup=backup)

            if self.activebookmark and self.activebookmark in repo._bookmarks:
                bookmarks.activate(repo, self.activebookmark)

        finally:
            clearstatus(repo)
            clearcollapsemsg(repo)
            if not suppwarns:
                repo.ui.warn(_(b'rebase aborted\n'))
        return 0


@command(
    b'rebase',
    [
        (
            b's',
            b'source',
            b'',
            _(b'rebase the specified changeset and descendants'),
            _(b'REV'),
        ),
        (
            b'b',
            b'base',
            b'',
            _(b'rebase everything from branching point of specified changeset'),
            _(b'REV'),
        ),
        (b'r', b'rev', [], _(b'rebase these revisions'), _(b'REV')),
        (
            b'd',
            b'dest',
            b'',
            _(b'rebase onto the specified changeset'),
            _(b'REV'),
        ),
        (b'', b'collapse', False, _(b'collapse the rebased changesets')),
        (
            b'm',
            b'message',
            b'',
            _(b'use text as collapse commit message'),
            _(b'TEXT'),
        ),
        (b'e', b'edit', False, _(b'invoke editor on commit messages')),
        (
            b'l',
            b'logfile',
            b'',
            _(b'read collapse commit message from file'),
            _(b'FILE'),
        ),
        (b'k', b'keep', False, _(b'keep original changesets')),
        (b'', b'keepbranches', False, _(b'keep original branch names')),
        (b'D', b'detach', False, _(b'(DEPRECATED)')),
        (b'i', b'interactive', False, _(b'(DEPRECATED)')),
        (b't', b'tool', b'', _(b'specify merge tool')),
        (b'', b'stop', False, _(b'stop interrupted rebase')),
        (b'c', b'continue', False, _(b'continue an interrupted rebase')),
        (b'a', b'abort', False, _(b'abort an interrupted rebase')),
        (
            b'',
            b'auto-orphans',
            b'',
            _(
                b'automatically rebase orphan revisions '
                b'in the specified revset (EXPERIMENTAL)'
            ),
        ),
    ]
    + cmdutil.dryrunopts
    + cmdutil.formatteropts
    + cmdutil.confirmopts,
    _(b'[-s REV | -b REV] [-d REV] [OPTION]'),
    helpcategory=command.CATEGORY_CHANGE_MANAGEMENT,
)
def rebase(ui, repo, **opts):
    """move changeset (and descendants) to a different branch

    Rebase uses repeated merging to graft changesets from one part of
    history (the source) onto another (the destination). This can be
    useful for linearizing *local* changes relative to a master
    development tree.

    Published commits cannot be rebased (see :hg:`help phases`).
    To copy commits, see :hg:`help graft`.

    If you don't specify a destination changeset (``-d/--dest``), rebase
    will use the same logic as :hg:`merge` to pick a destination.  if
    the current branch contains exactly one other head, the other head
    is merged with by default.  Otherwise, an explicit revision with
    which to merge with must be provided.  (destination changeset is not
    modified by rebasing, but new changesets are added as its
    descendants.)

    Here are the ways to select changesets:

      1. Explicitly select them using ``--rev``.

      2. Use ``--source`` to select a root changeset and include all of its
         descendants.

      3. Use ``--base`` to select a changeset; rebase will find ancestors
         and their descendants which are not also ancestors of the destination.

      4. If you do not specify any of ``--rev``, ``--source``, or ``--base``,
         rebase will use ``--base .`` as above.

    If ``--source`` or ``--rev`` is used, special names ``SRC`` and ``ALLSRC``
    can be used in ``--dest``. Destination would be calculated per source
    revision with ``SRC`` substituted by that single source revision and
    ``ALLSRC`` substituted by all source revisions.

    Rebase will destroy original changesets unless you use ``--keep``.
    It will also move your bookmarks (even if you do).

    Some changesets may be dropped if they do not contribute changes
    (e.g. merges from the destination branch).

    Unlike ``merge``, rebase will do nothing if you are at the branch tip of
    a named branch with two heads. You will need to explicitly specify source
    and/or destination.

    If you need to use a tool to automate merge/conflict decisions, you
    can specify one with ``--tool``, see :hg:`help merge-tools`.
    As a caveat: the tool will not be used to mediate when a file was
    deleted, there is no hook presently available for this.

    If a rebase is interrupted to manually resolve a conflict, it can be
    continued with --continue/-c, aborted with --abort/-a, or stopped with
    --stop.

    .. container:: verbose

      Examples:

      - move "local changes" (current commit back to branching point)
        to the current branch tip after a pull::

          hg rebase

      - move a single changeset to the stable branch::

          hg rebase -r 5f493448 -d stable

      - splice a commit and all its descendants onto another part of history::

          hg rebase --source c0c3 --dest 4cf9

      - rebase everything on a branch marked by a bookmark onto the
        default branch::

          hg rebase --base myfeature --dest default

      - collapse a sequence of changes into a single commit::

          hg rebase --collapse -r 1520:1525 -d .

      - move a named branch while preserving its name::

          hg rebase -r "branch(featureX)" -d 1.3 --keepbranches

      - stabilize orphaned changesets so history looks linear::

          hg rebase -r 'orphan()-obsolete()'\
 -d 'first(max((successors(max(roots(ALLSRC) & ::SRC)^)-obsolete())::) +\
 max(::((roots(ALLSRC) & ::SRC)^)-obsolete()))'

    Configuration Options:

    You can make rebase require a destination if you set the following config
    option::

      [commands]
      rebase.requiredest = True

    By default, rebase will close the transaction after each commit. For
    performance purposes, you can configure rebase to use a single transaction
    across the entire rebase. WARNING: This setting introduces a significant
    risk of losing the work you've done in a rebase if the rebase aborts
    unexpectedly::

      [rebase]
      singletransaction = True

    By default, rebase writes to the working copy, but you can configure it to
    run in-memory for better performance. When the rebase is not moving the
    parent(s) of the working copy (AKA the "currently checked out changesets"),
    this may also allow it to run even if the working copy is dirty::

      [rebase]
      experimental.inmemory = True

    Return Values:

    Returns 0 on success, 1 if nothing to rebase or there are
    unresolved conflicts.

    """
    opts = pycompat.byteskwargs(opts)
    inmemory = ui.configbool(b'rebase', b'experimental.inmemory')
    action = cmdutil.check_at_most_one_arg(opts, b'abort', b'stop', b'continue')
    if action:
        cmdutil.check_incompatible_arguments(
            opts, action, b'confirm', b'dry_run'
        )
        cmdutil.check_incompatible_arguments(
            opts, action, b'rev', b'source', b'base', b'dest'
        )
    cmdutil.check_at_most_one_arg(opts, b'confirm', b'dry_run')
    cmdutil.check_at_most_one_arg(opts, b'rev', b'source', b'base')

    if action or repo.currenttransaction() is not None:
        # in-memory rebase is not compatible with resuming rebases.
        # (Or if it is run within a transaction, since the restart logic can
        # fail the entire transaction.)
        inmemory = False

    if opts.get(b'auto_orphans'):
        disallowed_opts = set(opts) - {b'auto_orphans'}
        cmdutil.check_incompatible_arguments(
            opts, b'auto_orphans', *disallowed_opts
        )

        userrevs = list(repo.revs(opts.get(b'auto_orphans')))
        opts[b'rev'] = [revsetlang.formatspec(b'%ld and orphan()', userrevs)]
        opts[b'dest'] = b'_destautoorphanrebase(SRC)'

    if opts.get(b'dry_run') or opts.get(b'confirm'):
        return _dryrunrebase(ui, repo, action, opts)
    elif action == b'stop':
        rbsrt = rebaseruntime(repo, ui)
        with repo.wlock(), repo.lock():
            rbsrt.restorestatus()
            if rbsrt.collapsef:
                raise error.Abort(_(b"cannot stop in --collapse session"))
            allowunstable = obsolete.isenabled(repo, obsolete.allowunstableopt)
            if not (rbsrt.keepf or allowunstable):
                raise error.Abort(
                    _(
                        b"cannot remove original changesets with"
                        b" unrebased descendants"
                    ),
                    hint=_(
                        b'either enable obsmarkers to allow unstable '
                        b'revisions or use --keep to keep original '
                        b'changesets'
                    ),
                )
            # update to the current working revision
            # to clear interrupted merge
            hg.updaterepo(repo, rbsrt.originalwd, overwrite=True)
            rbsrt._finishrebase()
            return 0
    elif inmemory:
        try:
            # in-memory merge doesn't support conflicts, so if we hit any, abort
            # and re-run as an on-disk merge.
            overrides = {(b'rebase', b'singletransaction'): True}
            with ui.configoverride(overrides, b'rebase'):
                return _dorebase(ui, repo, action, opts, inmemory=inmemory)
        except error.InMemoryMergeConflictsError:
            ui.warn(
                _(
                    b'hit merge conflicts; re-running rebase without in-memory'
                    b' merge\n'
                )
            )
            # TODO: Make in-memory merge not use the on-disk merge state, so
            # we don't have to clean it here
            mergemod.mergestate.clean(repo)
            clearstatus(repo)
            clearcollapsemsg(repo)
            return _dorebase(ui, repo, action, opts, inmemory=False)
    else:
        return _dorebase(ui, repo, action, opts)


def _dryrunrebase(ui, repo, action, opts):
    rbsrt = rebaseruntime(repo, ui, inmemory=True, opts=opts)
    confirm = opts.get(b'confirm')
    if confirm:
        ui.status(_(b'starting in-memory rebase\n'))
    else:
        ui.status(
            _(b'starting dry-run rebase; repository will not be changed\n')
        )
    with repo.wlock(), repo.lock():
        needsabort = True
        try:
            overrides = {(b'rebase', b'singletransaction'): True}
            with ui.configoverride(overrides, b'rebase'):
                _origrebase(
                    ui,
                    repo,
                    action,
                    opts,
                    rbsrt,
                    inmemory=True,
                    leaveunfinished=True,
                )
        except error.InMemoryMergeConflictsError:
            ui.status(_(b'hit a merge conflict\n'))
            return 1
        except error.Abort:
            needsabort = False
            raise
        else:
            if confirm:
                ui.status(_(b'rebase completed successfully\n'))
                if not ui.promptchoice(_(b'apply changes (yn)?$$ &Yes $$ &No')):
                    # finish unfinished rebase
                    rbsrt._finishrebase()
                else:
                    rbsrt._prepareabortorcontinue(
                        isabort=True, backup=False, suppwarns=True
                    )
                needsabort = False
            else:
                ui.status(
                    _(
                        b'dry-run rebase completed successfully; run without'
                        b' -n/--dry-run to perform this rebase\n'
                    )
                )
            return 0
        finally:
            if needsabort:
                # no need to store backup in case of dryrun
                rbsrt._prepareabortorcontinue(
                    isabort=True, backup=False, suppwarns=True
                )


def _dorebase(ui, repo, action, opts, inmemory=False):
    rbsrt = rebaseruntime(repo, ui, inmemory, opts)
    return _origrebase(ui, repo, action, opts, rbsrt, inmemory=inmemory)


def _origrebase(
    ui, repo, action, opts, rbsrt, inmemory=False, leaveunfinished=False
):
    assert action != b'stop'
    with repo.wlock(), repo.lock():
        if opts.get(b'interactive'):
            try:
                if extensions.find(b'histedit'):
                    enablehistedit = b''
            except KeyError:
                enablehistedit = b" --config extensions.histedit="
            help = b"hg%s help -e histedit" % enablehistedit
            msg = (
                _(
                    b"interactive history editing is supported by the "
                    b"'histedit' extension (see \"%s\")"
                )
                % help
            )
            raise error.Abort(msg)

        if rbsrt.collapsemsg and not rbsrt.collapsef:
            raise error.Abort(_(b'message can only be specified with collapse'))

        if action:
            if rbsrt.collapsef:
                raise error.Abort(
                    _(b'cannot use collapse with continue or abort')
                )
            if action == b'abort' and opts.get(b'tool', False):
                ui.warn(_(b'tool option will be ignored\n'))
            if action == b'continue':
                ms = mergemod.mergestate.read(repo)
                mergeutil.checkunresolved(ms)

            retcode = rbsrt._prepareabortorcontinue(
                isabort=(action == b'abort')
            )
            if retcode is not None:
                return retcode
        else:
            # search default destination in this space
            # used in the 'hg pull --rebase' case, see issue 5214.
            destspace = opts.get(b'_destspace')
            destmap = _definedestmap(
                ui,
                repo,
                inmemory,
                opts.get(b'dest', None),
                opts.get(b'source', None),
                opts.get(b'base', None),
                opts.get(b'rev', []),
                destspace=destspace,
            )
            retcode = rbsrt._preparenewrebase(destmap)
            if retcode is not None:
                return retcode
            storecollapsemsg(repo, rbsrt.collapsemsg)

        tr = None

        singletr = ui.configbool(b'rebase', b'singletransaction')
        if singletr:
            tr = repo.transaction(b'rebase')

        # If `rebase.singletransaction` is enabled, wrap the entire operation in
        # one transaction here. Otherwise, transactions are obtained when
        # committing each node, which is slower but allows partial success.
        with util.acceptintervention(tr):
            # Same logic for the dirstate guard, except we don't create one when
            # rebasing in-memory (it's not needed).
            dsguard = None
            if singletr and not inmemory:
                dsguard = dirstateguard.dirstateguard(repo, b'rebase')
            with util.acceptintervention(dsguard):
                rbsrt._performrebase(tr)
                if not leaveunfinished:
                    rbsrt._finishrebase()


def _definedestmap(
    ui,
    repo,
    inmemory,
    destf=None,
    srcf=None,
    basef=None,
    revf=None,
    destspace=None,
):
    """use revisions argument to define destmap {srcrev: destrev}"""
    if revf is None:
        revf = []

    # destspace is here to work around issues with `hg pull --rebase` see
    # issue5214 for details

    cmdutil.checkunfinished(repo)
    if not inmemory:
        cmdutil.bailifchanged(repo)

    if ui.configbool(b'commands', b'rebase.requiredest') and not destf:
        raise error.Abort(
            _(b'you must specify a destination'),
            hint=_(b'use: hg rebase -d REV'),
        )

    dest = None

    if revf:
        rebaseset = scmutil.revrange(repo, revf)
        if not rebaseset:
            ui.status(_(b'empty "rev" revision set - nothing to rebase\n'))
            return None
    elif srcf:
        src = scmutil.revrange(repo, [srcf])
        if not src:
            ui.status(_(b'empty "source" revision set - nothing to rebase\n'))
            return None
        rebaseset = repo.revs(b'(%ld)::', src)
        assert rebaseset
    else:
        base = scmutil.revrange(repo, [basef or b'.'])
        if not base:
            ui.status(
                _(b'empty "base" revision set - ' b"can't compute rebase set\n")
            )
            return None
        if destf:
            # --base does not support multiple destinations
            dest = scmutil.revsingle(repo, destf)
        else:
            dest = repo[_destrebase(repo, base, destspace=destspace)]
            destf = bytes(dest)

        roots = []  # selected children of branching points
        bpbase = {}  # {branchingpoint: [origbase]}
        for b in base:  # group bases by branching points
            bp = repo.revs(b'ancestor(%d, %d)', b, dest.rev()).first()
            bpbase[bp] = bpbase.get(bp, []) + [b]
        if None in bpbase:
            # emulate the old behavior, showing "nothing to rebase" (a better
            # behavior may be abort with "cannot find branching point" error)
            bpbase.clear()
        for bp, bs in pycompat.iteritems(bpbase):  # calculate roots
            roots += list(repo.revs(b'children(%d) & ancestors(%ld)', bp, bs))

        rebaseset = repo.revs(b'%ld::', roots)

        if not rebaseset:
            # transform to list because smartsets are not comparable to
            # lists. This should be improved to honor laziness of
            # smartset.
            if list(base) == [dest.rev()]:
                if basef:
                    ui.status(
                        _(
                            b'nothing to rebase - %s is both "base"'
                            b' and destination\n'
                        )
                        % dest
                    )
                else:
                    ui.status(
                        _(
                            b'nothing to rebase - working directory '
                            b'parent is also destination\n'
                        )
                    )
            elif not repo.revs(b'%ld - ::%d', base, dest.rev()):
                if basef:
                    ui.status(
                        _(
                            b'nothing to rebase - "base" %s is '
                            b'already an ancestor of destination '
                            b'%s\n'
                        )
                        % (b'+'.join(bytes(repo[r]) for r in base), dest)
                    )
                else:
                    ui.status(
                        _(
                            b'nothing to rebase - working '
                            b'directory parent is already an '
                            b'ancestor of destination %s\n'
                        )
                        % dest
                    )
            else:  # can it happen?
                ui.status(
                    _(b'nothing to rebase from %s to %s\n')
                    % (b'+'.join(bytes(repo[r]) for r in base), dest)
                )
            return None

    rebasingwcp = repo[b'.'].rev() in rebaseset
    ui.log(
        b"rebase",
        b"rebasing working copy parent: %r\n",
        rebasingwcp,
        rebase_rebasing_wcp=rebasingwcp,
    )
    if inmemory and rebasingwcp:
        # Check these since we did not before.
        cmdutil.checkunfinished(repo)
        cmdutil.bailifchanged(repo)

    if not destf:
        dest = repo[_destrebase(repo, rebaseset, destspace=destspace)]
        destf = bytes(dest)

    allsrc = revsetlang.formatspec(b'%ld', rebaseset)
    alias = {b'ALLSRC': allsrc}

    if dest is None:
        try:
            # fast path: try to resolve dest without SRC alias
            dest = scmutil.revsingle(repo, destf, localalias=alias)
        except error.RepoLookupError:
            # multi-dest path: resolve dest for each SRC separately
            destmap = {}
            for r in rebaseset:
                alias[b'SRC'] = revsetlang.formatspec(b'%d', r)
                # use repo.anyrevs instead of scmutil.revsingle because we
                # don't want to abort if destset is empty.
                destset = repo.anyrevs([destf], user=True, localalias=alias)
                size = len(destset)
                if size == 1:
                    destmap[r] = destset.first()
                elif size == 0:
                    ui.note(_(b'skipping %s - empty destination\n') % repo[r])
                else:
                    raise error.Abort(
                        _(b'rebase destination for %s is not unique') % repo[r]
                    )

    if dest is not None:
        # single-dest case: assign dest to each rev in rebaseset
        destrev = dest.rev()
        destmap = {r: destrev for r in rebaseset}  # {srcrev: destrev}

    if not destmap:
        ui.status(_(b'nothing to rebase - empty destination\n'))
        return None

    return destmap


def externalparent(repo, state, destancestors):
    """Return the revision that should be used as the second parent
    when the revisions in state is collapsed on top of destancestors.
    Abort if there is more than one parent.
    """
    parents = set()
    source = min(state)
    for rev in state:
        if rev == source:
            continue
        for p in repo[rev].parents():
            if p.rev() not in state and p.rev() not in destancestors:
                parents.add(p.rev())
    if not parents:
        return nullrev
    if len(parents) == 1:
        return parents.pop()
    raise error.Abort(
        _(
            b'unable to collapse on top of %d, there is more '
            b'than one external parent: %s'
        )
        % (max(destancestors), b', '.join(b"%d" % p for p in sorted(parents)))
    )


def commitmemorynode(repo, p1, p2, wctx, editor, extra, user, date, commitmsg):
    '''Commit the memory changes with parents p1 and p2.
    Return node of committed revision.'''
    # Replicates the empty check in ``repo.commit``.
    if wctx.isempty() and not repo.ui.configbool(b'ui', b'allowemptycommit'):
        return None

    # By convention, ``extra['branch']`` (set by extrafn) clobbers
    # ``branch`` (used when passing ``--keepbranches``).
    branch = None
    if b'branch' in extra:
        branch = extra[b'branch']

    wctx.setparents(repo[p1].node(), repo[p2].node())
    memctx = wctx.tomemctx(
        commitmsg,
        date=date,
        extra=extra,
        user=user,
        branch=branch,
        editor=editor,
    )
    commitres = repo.commitctx(memctx)
    wctx.clean()  # Might be reused
    return commitres


def commitnode(repo, p1, p2, editor, extra, user, date, commitmsg):
    '''Commit the wd changes with parents p1 and p2.
    Return node of committed revision.'''
    dsguard = util.nullcontextmanager()
    if not repo.ui.configbool(b'rebase', b'singletransaction'):
        dsguard = dirstateguard.dirstateguard(repo, b'rebase')
    with dsguard:
        repo.setparents(repo[p1].node(), repo[p2].node())

        # Commit might fail if unresolved files exist
        newnode = repo.commit(
            text=commitmsg, user=user, date=date, extra=extra, editor=editor
        )

        repo.dirstate.setbranch(repo[newnode].branch())
        return newnode


def rebasenode(repo, rev, p1, base, collapse, dest, wctx):
    """Rebase a single revision rev on top of p1 using base as merge ancestor"""
    # Merge phase
    # Update to destination and merge it with local
    p1ctx = repo[p1]
    if wctx.isinmemory():
        wctx.setbase(p1ctx)
    else:
        if repo[b'.'].rev() != p1:
            repo.ui.debug(b" update to %d:%s\n" % (p1, p1ctx))
            mergemod.update(repo, p1, branchmerge=False, force=True)
        else:
            repo.ui.debug(b" already in destination\n")
        # This is, alas, necessary to invalidate workingctx's manifest cache,
        # as well as other data we litter on it in other places.
        wctx = repo[None]
        repo.dirstate.write(repo.currenttransaction())
    ctx = repo[rev]
    repo.ui.debug(b" merge against %d:%s\n" % (rev, ctx))
    if base is not None:
        repo.ui.debug(b"   detach base %d:%s\n" % (base, repo[base]))

    # See explanation in merge.graft()
    mergeancestor = repo.changelog.isancestor(p1ctx.node(), ctx.node())
    stats = mergemod.update(
        repo,
        rev,
        branchmerge=True,
        force=True,
        ancestor=base,
        mergeancestor=mergeancestor,
        labels=[b'dest', b'source'],
        wc=wctx,
    )
    if collapse:
        copies.graftcopies(wctx, ctx, repo[dest])
    else:
        # If we're not using --collapse, we need to
        # duplicate copies between the revision we're
        # rebasing and its first parent.
        copies.graftcopies(wctx, ctx, ctx.p1())
    return stats


def adjustdest(repo, rev, destmap, state, skipped):
    r"""adjust rebase destination given the current rebase state

    rev is what is being rebased. Return a list of two revs, which are the
    adjusted destinations for rev's p1 and p2, respectively. If a parent is
    nullrev, return dest without adjustment for it.

    For example, when doing rebasing B+E to F, C to G, rebase will first move B
    to B1, and E's destination will be adjusted from F to B1.

        B1 <- written during rebasing B
        |
        F <- original destination of B, E
        |
        | E <- rev, which is being rebased
        | |
        | D <- prev, one parent of rev being checked
        | |
        | x <- skipped, ex. no successor or successor in (::dest)
        | |
        | C <- rebased as C', different destination
        | |
        | B <- rebased as B1     C'
        |/                       |
        A                        G <- destination of C, different

    Another example about merge changeset, rebase -r C+G+H -d K, rebase will
    first move C to C1, G to G1, and when it's checking H, the adjusted
    destinations will be [C1, G1].

            H       C1 G1
           /|       | /
          F G       |/
        K | |  ->   K
        | C D       |
        | |/        |
        | B         | ...
        |/          |/
        A           A

    Besides, adjust dest according to existing rebase information. For example,

      B C D    B needs to be rebased on top of C, C needs to be rebased on top
       \|/     of D. We will rebase C first.
        A

          C'   After rebasing C, when considering B's destination, use C'
          |    instead of the original C.
      B   D
       \ /
        A
    """
    # pick already rebased revs with same dest from state as interesting source
    dest = destmap[rev]
    source = [
        s
        for s, d in state.items()
        if d > 0 and destmap[s] == dest and s not in skipped
    ]

    result = []
    for prev in repo.changelog.parentrevs(rev):
        adjusted = dest
        if prev != nullrev:
            candidate = repo.revs(b'max(%ld and (::%d))', source, prev).first()
            if candidate is not None:
                adjusted = state[candidate]
        if adjusted == dest and dest in state:
            adjusted = state[dest]
            if adjusted == revtodo:
                # sortsource should produce an order that makes this impossible
                raise error.ProgrammingError(
                    b'rev %d should be rebased already at this time' % dest
                )
        result.append(adjusted)
    return result


def _checkobsrebase(repo, ui, rebaseobsrevs, rebaseobsskipped):
    """
    Abort if rebase will create divergence or rebase is noop because of markers

    `rebaseobsrevs`: set of obsolete revision in source
    `rebaseobsskipped`: set of revisions from source skipped because they have
    successors in destination or no non-obsolete successor.
    """
    # Obsolete node with successors not in dest leads to divergence
    divergenceok = ui.configbool(b'experimental', b'evolution.allowdivergence')
    divergencebasecandidates = rebaseobsrevs - rebaseobsskipped

    if divergencebasecandidates and not divergenceok:
        divhashes = (bytes(repo[r]) for r in divergencebasecandidates)
        msg = _(b"this rebase will cause divergences from: %s")
        h = _(
            b"to force the rebase please set "
            b"experimental.evolution.allowdivergence=True"
        )
        raise error.Abort(msg % (b",".join(divhashes),), hint=h)


def successorrevs(unfi, rev):
    """yield revision numbers for successors of rev"""
    assert unfi.filtername is None
    get_rev = unfi.changelog.index.get_rev
    for s in obsutil.allsuccessors(unfi.obsstore, [unfi[rev].node()]):
        r = get_rev(s)
        if r is not None:
            yield r


def defineparents(repo, rev, destmap, state, skipped, obsskipped):
    """Return new parents and optionally a merge base for rev being rebased

    The destination specified by "dest" cannot always be used directly because
    previously rebase result could affect destination. For example,

          D E    rebase -r C+D+E -d B
          |/     C will be rebased to C'
        B C      D's new destination will be C' instead of B
        |/       E's new destination will be C' instead of B
        A

    The new parents of a merge is slightly more complicated. See the comment
    block below.
    """
    # use unfiltered changelog since successorrevs may return filtered nodes
    assert repo.filtername is None
    cl = repo.changelog
    isancestor = cl.isancestorrev

    dest = destmap[rev]
    oldps = repo.changelog.parentrevs(rev)  # old parents
    newps = [nullrev, nullrev]  # new parents
    dests = adjustdest(repo, rev, destmap, state, skipped)
    bases = list(oldps)  # merge base candidates, initially just old parents

    if all(r == nullrev for r in oldps[1:]):
        # For non-merge changeset, just move p to adjusted dest as requested.
        newps[0] = dests[0]
    else:
        # For merge changeset, if we move p to dests[i] unconditionally, both
        # parents may change and the end result looks like "the merge loses a
        # parent", which is a surprise. This is a limit because "--dest" only
        # accepts one dest per src.
        #
        # Therefore, only move p with reasonable conditions (in this order):
        #   1. use dest, if dest is a descendent of (p or one of p's successors)
        #   2. use p's rebased result, if p is rebased (state[p] > 0)
        #
        # Comparing with adjustdest, the logic here does some additional work:
        #   1. decide which parents will not be moved towards dest
        #   2. if the above decision is "no", should a parent still be moved
        #      because it was rebased?
        #
        # For example:
        #
        #     C    # "rebase -r C -d D" is an error since none of the parents
        #    /|    # can be moved. "rebase -r B+C -d D" will move C's parent
        #   A B D  # B (using rule "2."), since B will be rebased.
        #
        # The loop tries to be not rely on the fact that a Mercurial node has
        # at most 2 parents.
        for i, p in enumerate(oldps):
            np = p  # new parent
            if any(isancestor(x, dests[i]) for x in successorrevs(repo, p)):
                np = dests[i]
            elif p in state and state[p] > 0:
                np = state[p]

            # "bases" only record "special" merge bases that cannot be
            # calculated from changelog DAG (i.e. isancestor(p, np) is False).
            # For example:
            #
            #   B'   # rebase -s B -d D, when B was rebased to B'. dest for C
            #   | C  # is B', but merge base for C is B, instead of
            #   D |  # changelog.ancestor(C, B') == A. If changelog DAG and
            #   | B  # "state" edges are merged (so there will be an edge from
            #   |/   # B to B'), the merge base is still ancestor(C, B') in
            #   A    # the merged graph.
            #
            # Also see https://bz.mercurial-scm.org/show_bug.cgi?id=1950#c8
            # which uses "virtual null merge" to explain this situation.
            if isancestor(p, np):
                bases[i] = nullrev

            # If one parent becomes an ancestor of the other, drop the ancestor
            for j, x in enumerate(newps[:i]):
                if x == nullrev:
                    continue
                if isancestor(np, x):  # CASE-1
                    np = nullrev
                elif isancestor(x, np):  # CASE-2
                    newps[j] = np
                    np = nullrev
                    # New parents forming an ancestor relationship does not
                    # mean the old parents have a similar relationship. Do not
                    # set bases[x] to nullrev.
                    bases[j], bases[i] = bases[i], bases[j]

            newps[i] = np

        # "rebasenode" updates to new p1, and the old p1 will be used as merge
        # base. If only p2 changes, merging using unchanged p1 as merge base is
        # suboptimal. Therefore swap parents to make the merge sane.
        if newps[1] != nullrev and oldps[0] == newps[0]:
            assert len(newps) == 2 and len(oldps) == 2
            newps.reverse()
            bases.reverse()

        # No parent change might be an error because we fail to make rev a
        # descendent of requested dest. This can happen, for example:
        #
        #     C    # rebase -r C -d D
        #    /|    # None of A and B will be changed to D and rebase fails.
        #   A B D
        if set(newps) == set(oldps) and dest not in newps:
            raise error.Abort(
                _(
                    b'cannot rebase %d:%s without '
                    b'moving at least one of its parents'
                )
                % (rev, repo[rev])
            )

    # Source should not be ancestor of dest. The check here guarantees it's
    # impossible. With multi-dest, the initial check does not cover complex
    # cases since we don't have abstractions to dry-run rebase cheaply.
    if any(p != nullrev and isancestor(rev, p) for p in newps):
        raise error.Abort(_(b'source is ancestor of destination'))

    # "rebasenode" updates to new p1, use the corresponding merge base.
    if bases[0] != nullrev:
        base = bases[0]
    else:
        base = None

    # Check if the merge will contain unwanted changes. That may happen if
    # there are multiple special (non-changelog ancestor) merge bases, which
    # cannot be handled well by the 3-way merge algorithm. For example:
    #
    #     F
    #    /|
    #   D E  # "rebase -r D+E+F -d Z", when rebasing F, if "D" was chosen
    #   | |  # as merge base, the difference between D and F will include
    #   B C  # C, so the rebased F will contain C surprisingly. If "E" was
    #   |/   #  chosen, the rebased F will contain B.
    #   A Z
    #
    # But our merge base candidates (D and E in above case) could still be
    # better than the default (ancestor(F, Z) == null). Therefore still
    # pick one (so choose p1 above).
    if sum(1 for b in set(bases) if b != nullrev) > 1:
        unwanted = [None, None]  # unwanted[i]: unwanted revs if choose bases[i]
        for i, base in enumerate(bases):
            if base == nullrev:
                continue
            # Revisions in the side (not chosen as merge base) branch that
            # might contain "surprising" contents
            siderevs = list(
                repo.revs(b'((%ld-%d) %% (%d+%d))', bases, base, base, dest)
            )

            # If those revisions are covered by rebaseset, the result is good.
            # A merge in rebaseset would be considered to cover its ancestors.
            if siderevs:
                rebaseset = [
                    r for r, d in state.items() if d > 0 and r not in obsskipped
                ]
                merges = [
                    r for r in rebaseset if cl.parentrevs(r)[1] != nullrev
                ]
                unwanted[i] = list(
                    repo.revs(
                        b'%ld - (::%ld) - %ld', siderevs, merges, rebaseset
                    )
                )

        # Choose a merge base that has a minimal number of unwanted revs.
        l, i = min(
            (len(revs), i)
            for i, revs in enumerate(unwanted)
            if revs is not None
        )
        base = bases[i]

        # newps[0] should match merge base if possible. Currently, if newps[i]
        # is nullrev, the only case is newps[i] and newps[j] (j < i), one is
        # the other's ancestor. In that case, it's fine to not swap newps here.
        # (see CASE-1 and CASE-2 above)
        if i != 0 and newps[i] != nullrev:
            newps[0], newps[i] = newps[i], newps[0]

        # The merge will include unwanted revisions. Abort now. Revisit this if
        # we have a more advanced merge algorithm that handles multiple bases.
        if l > 0:
            unwanteddesc = _(b' or ').join(
                (
                    b', '.join(b'%d:%s' % (r, repo[r]) for r in revs)
                    for revs in unwanted
                    if revs is not None
                )
            )
            raise error.Abort(
                _(b'rebasing %d:%s will include unwanted changes from %s')
                % (rev, repo[rev], unwanteddesc)
            )

    repo.ui.debug(b" future parents are %d and %d\n" % tuple(newps))

    return newps[0], newps[1], base


def isagitpatch(repo, patchname):
    """Return true if the given patch is in git format"""
    mqpatch = os.path.join(repo.mq.path, patchname)
    for line in patch.linereader(open(mqpatch, b'rb')):
        if line.startswith(b'diff --git'):
            return True
    return False


def updatemq(repo, state, skipped, **opts):
    """Update rebased mq patches - finalize and then import them"""
    mqrebase = {}
    mq = repo.mq
    original_series = mq.fullseries[:]
    skippedpatches = set()

    for p in mq.applied:
        rev = repo[p.node].rev()
        if rev in state:
            repo.ui.debug(
                b'revision %d is an mq patch (%s), finalize it.\n'
                % (rev, p.name)
            )
            mqrebase[rev] = (p.name, isagitpatch(repo, p.name))
        else:
            # Applied but not rebased, not sure this should happen
            skippedpatches.add(p.name)

    if mqrebase:
        mq.finish(repo, mqrebase.keys())

        # We must start import from the newest revision
        for rev in sorted(mqrebase, reverse=True):
            if rev not in skipped:
                name, isgit = mqrebase[rev]
                repo.ui.note(
                    _(b'updating mq patch %s to %d:%s\n')
                    % (name, state[rev], repo[state[rev]])
                )
                mq.qimport(
                    repo,
                    (),
                    patchname=name,
                    git=isgit,
                    rev=[b"%d" % state[rev]],
                )
            else:
                # Rebased and skipped
                skippedpatches.add(mqrebase[rev][0])

        # Patches were either applied and rebased and imported in
        # order, applied and removed or unapplied. Discard the removed
        # ones while preserving the original series order and guards.
        newseries = [
            s
            for s in original_series
            if mq.guard_re.split(s, 1)[0] not in skippedpatches
        ]
        mq.fullseries[:] = newseries
        mq.seriesdirty = True
        mq.savedirty()


def storecollapsemsg(repo, collapsemsg):
    """Store the collapse message to allow recovery"""
    collapsemsg = collapsemsg or b''
    f = repo.vfs(b"last-message.txt", b"w")
    f.write(b"%s\n" % collapsemsg)
    f.close()


def clearcollapsemsg(repo):
    """Remove collapse message file"""
    repo.vfs.unlinkpath(b"last-message.txt", ignoremissing=True)


def restorecollapsemsg(repo, isabort):
    """Restore previously stored collapse message"""
    try:
        f = repo.vfs(b"last-message.txt")
        collapsemsg = f.readline().strip()
        f.close()
    except IOError as err:
        if err.errno != errno.ENOENT:
            raise
        if isabort:
            # Oh well, just abort like normal
            collapsemsg = b''
        else:
            raise error.Abort(_(b'missing .hg/last-message.txt for rebase'))
    return collapsemsg


def clearstatus(repo):
    """Remove the status files"""
    # Make sure the active transaction won't write the state file
    tr = repo.currenttransaction()
    if tr:
        tr.removefilegenerator(b'rebasestate')
    repo.vfs.unlinkpath(b"rebasestate", ignoremissing=True)


def sortsource(destmap):
    """yield source revisions in an order that we only rebase things once

    If source and destination overlaps, we should filter out revisions
    depending on other revisions which hasn't been rebased yet.

    Yield a sorted list of revisions each time.

    For example, when rebasing A to B, B to C. This function yields [B], then
    [A], indicating B needs to be rebased first.

    Raise if there is a cycle so the rebase is impossible.
    """
    srcset = set(destmap)
    while srcset:
        srclist = sorted(srcset)
        result = []
        for r in srclist:
            if destmap[r] not in srcset:
                result.append(r)
        if not result:
            raise error.Abort(_(b'source and destination form a cycle'))
        srcset -= set(result)
        yield result


def buildstate(repo, destmap, collapse):
    '''Define which revisions are going to be rebased and where

    repo: repo
    destmap: {srcrev: destrev}
    '''
    rebaseset = destmap.keys()
    originalwd = repo[b'.'].rev()

    # This check isn't strictly necessary, since mq detects commits over an
    # applied patch. But it prevents messing up the working directory when
    # a partially completed rebase is blocked by mq.
    if b'qtip' in repo.tags():
        mqapplied = set(repo[s.node].rev() for s in repo.mq.applied)
        if set(destmap.values()) & mqapplied:
            raise error.Abort(_(b'cannot rebase onto an applied mq patch'))

    # Get "cycle" error early by exhausting the generator.
    sortedsrc = list(sortsource(destmap))  # a list of sorted revs
    if not sortedsrc:
        raise error.Abort(_(b'no matching revisions'))

    # Only check the first batch of revisions to rebase not depending on other
    # rebaseset. This means "source is ancestor of destination" for the second
    # (and following) batches of revisions are not checked here. We rely on
    # "defineparents" to do that check.
    roots = list(repo.set(b'roots(%ld)', sortedsrc[0]))
    if not roots:
        raise error.Abort(_(b'no matching revisions'))

    def revof(r):
        return r.rev()

    roots = sorted(roots, key=revof)
    state = dict.fromkeys(rebaseset, revtodo)
    emptyrebase = len(sortedsrc) == 1
    for root in roots:
        dest = repo[destmap[root.rev()]]
        commonbase = root.ancestor(dest)
        if commonbase == root:
            raise error.Abort(_(b'source is ancestor of destination'))
        if commonbase == dest:
            wctx = repo[None]
            if dest == wctx.p1():
                # when rebasing to '.', it will use the current wd branch name
                samebranch = root.branch() == wctx.branch()
            else:
                samebranch = root.branch() == dest.branch()
            if not collapse and samebranch and dest in root.parents():
                # mark the revision as done by setting its new revision
                # equal to its old (current) revisions
                state[root.rev()] = root.rev()
                repo.ui.debug(b'source is a child of destination\n')
                continue

        emptyrebase = False
        repo.ui.debug(b'rebase onto %s starting from %s\n' % (dest, root))
    if emptyrebase:
        return None
    for rev in sorted(state):
        parents = [p for p in repo.changelog.parentrevs(rev) if p != nullrev]
        # if all parents of this revision are done, then so is this revision
        if parents and all((state.get(p) == p for p in parents)):
            state[rev] = rev
    return originalwd, destmap, state


def clearrebased(
    ui,
    repo,
    destmap,
    state,
    skipped,
    collapsedas=None,
    keepf=False,
    fm=None,
    backup=True,
):
    """dispose of rebased revision at the end of the rebase

    If `collapsedas` is not None, the rebase was a collapse whose result if the
    `collapsedas` node.

    If `keepf` is not True, the rebase has --keep set and no nodes should be
    removed (but bookmarks still need to be moved).

    If `backup` is False, no backup will be stored when stripping rebased
    revisions.
    """
    tonode = repo.changelog.node
    replacements = {}
    moves = {}
    stripcleanup = not obsolete.isenabled(repo, obsolete.createmarkersopt)

    collapsednodes = []
    for rev, newrev in sorted(state.items()):
        if newrev >= 0 and newrev != rev:
            oldnode = tonode(rev)
            newnode = collapsedas or tonode(newrev)
            moves[oldnode] = newnode
            succs = None
            if rev in skipped:
                if stripcleanup or not repo[rev].obsolete():
                    succs = ()
            elif collapsedas:
                collapsednodes.append(oldnode)
            else:
                succs = (newnode,)
            if succs is not None:
                replacements[(oldnode,)] = succs
    if collapsednodes:
        replacements[tuple(collapsednodes)] = (collapsedas,)
    if fm:
        hf = fm.hexfunc
        fl = fm.formatlist
        fd = fm.formatdict
        changes = {}
        for oldns, newn in pycompat.iteritems(replacements):
            for oldn in oldns:
                changes[hf(oldn)] = fl([hf(n) for n in newn], name=b'node')
        nodechanges = fd(changes, key=b"oldnode", value=b"newnodes")
        fm.data(nodechanges=nodechanges)
    if keepf:
        replacements = {}
    scmutil.cleanupnodes(repo, replacements, b'rebase', moves, backup=backup)


def pullrebase(orig, ui, repo, *args, **opts):
    """Call rebase after pull if the latter has been invoked with --rebase"""
    if opts.get('rebase'):
        if ui.configbool(b'commands', b'rebase.requiredest'):
            msg = _(b'rebase destination required by configuration')
            hint = _(b'use hg pull followed by hg rebase -d DEST')
            raise error.Abort(msg, hint=hint)

        with repo.wlock(), repo.lock():
            if opts.get('update'):
                del opts['update']
                ui.debug(
                    b'--update and --rebase are not compatible, ignoring '
                    b'the update flag\n'
                )

            cmdutil.checkunfinished(repo, skipmerge=True)
            cmdutil.bailifchanged(
                repo,
                hint=_(
                    b'cannot pull with rebase: '
                    b'please commit or shelve your changes first'
                ),
            )

            revsprepull = len(repo)
            origpostincoming = commands.postincoming

            def _dummy(*args, **kwargs):
                pass

            commands.postincoming = _dummy
            try:
                ret = orig(ui, repo, *args, **opts)
            finally:
                commands.postincoming = origpostincoming
            revspostpull = len(repo)
            if revspostpull > revsprepull:
                # --rev option from pull conflict with rebase own --rev
                # dropping it
                if 'rev' in opts:
                    del opts['rev']
                # positional argument from pull conflicts with rebase's own
                # --source.
                if 'source' in opts:
                    del opts['source']
                # revsprepull is the len of the repo, not revnum of tip.
                destspace = list(repo.changelog.revs(start=revsprepull))
                opts['_destspace'] = destspace
                try:
                    rebase(ui, repo, **opts)
                except error.NoMergeDestAbort:
                    # we can maybe update instead
                    rev, _a, _b = destutil.destupdate(repo)
                    if rev == repo[b'.'].rev():
                        ui.status(_(b'nothing to rebase\n'))
                    else:
                        ui.status(_(b'nothing to rebase - updating instead\n'))
                        # not passing argument to get the bare update behavior
                        # with warning and trumpets
                        commands.update(ui, repo)
    else:
        if opts.get('tool'):
            raise error.Abort(_(b'--tool can only be used with --rebase'))
        ret = orig(ui, repo, *args, **opts)

    return ret


def _filterobsoleterevs(repo, revs):
    """returns a set of the obsolete revisions in revs"""
    return set(r for r in revs if repo[r].obsolete())


def _computeobsoletenotrebased(repo, rebaseobsrevs, destmap):
    """Return (obsoletenotrebased, obsoletewithoutsuccessorindestination).

    `obsoletenotrebased` is a mapping mapping obsolete => successor for all
    obsolete nodes to be rebased given in `rebaseobsrevs`.

    `obsoletewithoutsuccessorindestination` is a set with obsolete revisions
    without a successor in destination.

    `obsoleteextinctsuccessors` is a set of obsolete revisions with only
    obsolete successors.
    """
    obsoletenotrebased = {}
    obsoletewithoutsuccessorindestination = set()
    obsoleteextinctsuccessors = set()

    assert repo.filtername is None
    cl = repo.changelog
    get_rev = cl.index.get_rev
    extinctrevs = set(repo.revs(b'extinct()'))
    for srcrev in rebaseobsrevs:
        srcnode = cl.node(srcrev)
        # XXX: more advanced APIs are required to handle split correctly
        successors = set(obsutil.allsuccessors(repo.obsstore, [srcnode]))
        # obsutil.allsuccessors includes node itself
        successors.remove(srcnode)
        succrevs = {get_rev(s) for s in successors}
        succrevs.discard(None)
        if succrevs.issubset(extinctrevs):
            # all successors are extinct
            obsoleteextinctsuccessors.add(srcrev)
        if not successors:
            # no successor
            obsoletenotrebased[srcrev] = None
        else:
            dstrev = destmap[srcrev]
            for succrev in succrevs:
                if cl.isancestorrev(succrev, dstrev):
                    obsoletenotrebased[srcrev] = succrev
                    break
            else:
                # If 'srcrev' has a successor in rebase set but none in
                # destination (which would be catched above), we shall skip it
                # and its descendants to avoid divergence.
                if srcrev in extinctrevs or any(s in destmap for s in succrevs):
                    obsoletewithoutsuccessorindestination.add(srcrev)

    return (
        obsoletenotrebased,
        obsoletewithoutsuccessorindestination,
        obsoleteextinctsuccessors,
    )


def abortrebase(ui, repo):
    with repo.wlock(), repo.lock():
        rbsrt = rebaseruntime(repo, ui)
        rbsrt._prepareabortorcontinue(isabort=True)


def continuerebase(ui, repo):
    with repo.wlock(), repo.lock():
        rbsrt = rebaseruntime(repo, ui)
        ms = mergemod.mergestate.read(repo)
        mergeutil.checkunresolved(ms)
        retcode = rbsrt._prepareabortorcontinue(isabort=False)
        if retcode is not None:
            return retcode
        rbsrt._performrebase(None)
        rbsrt._finishrebase()


def summaryhook(ui, repo):
    if not repo.vfs.exists(b'rebasestate'):
        return
    try:
        rbsrt = rebaseruntime(repo, ui, {})
        rbsrt.restorestatus()
        state = rbsrt.state
    except error.RepoLookupError:
        # i18n: column positioning for "hg summary"
        msg = _(b'rebase: (use "hg rebase --abort" to clear broken state)\n')
        ui.write(msg)
        return
    numrebased = len([i for i in pycompat.itervalues(state) if i >= 0])
    # i18n: column positioning for "hg summary"
    ui.write(
        _(b'rebase: %s, %s (rebase --continue)\n')
        % (
            ui.label(_(b'%d rebased'), b'rebase.rebased') % numrebased,
            ui.label(_(b'%d remaining'), b'rebase.remaining')
            % (len(state) - numrebased),
        )
    )


def uisetup(ui):
    # Replace pull with a decorator to provide --rebase option
    entry = extensions.wrapcommand(commands.table, b'pull', pullrebase)
    entry[1].append(
        (b'', b'rebase', None, _(b"rebase working directory to branch head"))
    )
    entry[1].append((b't', b'tool', b'', _(b"specify merge tool for rebase")))
    cmdutil.summaryhooks.add(b'rebase', summaryhook)
    statemod.addunfinished(
        b'rebase',
        fname=b'rebasestate',
        stopflag=True,
        continueflag=True,
        abortfunc=abortrebase,
        continuefunc=continuerebase,
    )
