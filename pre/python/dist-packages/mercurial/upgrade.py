# upgrade.py - functions for in place upgrade of Mercurial repository
#
# Copyright (c) 2016-present, Gregory Szorc
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

import stat

from .i18n import _
from .pycompat import getattr
from . import (
    changelog,
    copies,
    error,
    filelog,
    hg,
    localrepo,
    manifest,
    pycompat,
    revlog,
    scmutil,
    util,
    vfs as vfsmod,
)

from .utils import compression

# list of requirements that request a clone of all revlog if added/removed
RECLONES_REQUIREMENTS = {
    b'generaldelta',
    localrepo.SPARSEREVLOG_REQUIREMENT,
}


def requiredsourcerequirements(repo):
    """Obtain requirements required to be present to upgrade a repo.

    An upgrade will not be allowed if the repository doesn't have the
    requirements returned by this function.
    """
    return {
        # Introduced in Mercurial 0.9.2.
        b'revlogv1',
        # Introduced in Mercurial 0.9.2.
        b'store',
    }


def blocksourcerequirements(repo):
    """Obtain requirements that will prevent an upgrade from occurring.

    An upgrade cannot be performed if the source repository contains a
    requirements in the returned set.
    """
    return {
        # The upgrade code does not yet support these experimental features.
        # This is an artificial limitation.
        b'treemanifest',
        # This was a precursor to generaldelta and was never enabled by default.
        # It should (hopefully) not exist in the wild.
        b'parentdelta',
        # Upgrade should operate on the actual store, not the shared link.
        b'shared',
    }


def supportremovedrequirements(repo):
    """Obtain requirements that can be removed during an upgrade.

    If an upgrade were to create a repository that dropped a requirement,
    the dropped requirement must appear in the returned set for the upgrade
    to be allowed.
    """
    supported = {
        localrepo.SPARSEREVLOG_REQUIREMENT,
        localrepo.SIDEDATA_REQUIREMENT,
        localrepo.COPIESSDC_REQUIREMENT,
    }
    for name in compression.compengines:
        engine = compression.compengines[name]
        if engine.available() and engine.revlogheader():
            supported.add(b'exp-compression-%s' % name)
            if engine.name() == b'zstd':
                supported.add(b'revlog-compression-zstd')
    return supported


def supporteddestrequirements(repo):
    """Obtain requirements that upgrade supports in the destination.

    If the result of the upgrade would create requirements not in this set,
    the upgrade is disallowed.

    Extensions should monkeypatch this to add their custom requirements.
    """
    supported = {
        b'dotencode',
        b'fncache',
        b'generaldelta',
        b'revlogv1',
        b'store',
        localrepo.SPARSEREVLOG_REQUIREMENT,
        localrepo.SIDEDATA_REQUIREMENT,
        localrepo.COPIESSDC_REQUIREMENT,
    }
    for name in compression.compengines:
        engine = compression.compengines[name]
        if engine.available() and engine.revlogheader():
            supported.add(b'exp-compression-%s' % name)
            if engine.name() == b'zstd':
                supported.add(b'revlog-compression-zstd')
    return supported


def allowednewrequirements(repo):
    """Obtain requirements that can be added to a repository during upgrade.

    This is used to disallow proposed requirements from being added when
    they weren't present before.

    We use a list of allowed requirement additions instead of a list of known
    bad additions because the whitelist approach is safer and will prevent
    future, unknown requirements from accidentally being added.
    """
    supported = {
        b'dotencode',
        b'fncache',
        b'generaldelta',
        localrepo.SPARSEREVLOG_REQUIREMENT,
        localrepo.SIDEDATA_REQUIREMENT,
        localrepo.COPIESSDC_REQUIREMENT,
    }
    for name in compression.compengines:
        engine = compression.compengines[name]
        if engine.available() and engine.revlogheader():
            supported.add(b'exp-compression-%s' % name)
            if engine.name() == b'zstd':
                supported.add(b'revlog-compression-zstd')
    return supported


def preservedrequirements(repo):
    return set()


deficiency = b'deficiency'
optimisation = b'optimization'


class improvement(object):
    """Represents an improvement that can be made as part of an upgrade.

    The following attributes are defined on each instance:

    name
       Machine-readable string uniquely identifying this improvement. It
       will be mapped to an action later in the upgrade process.

    type
       Either ``deficiency`` or ``optimisation``. A deficiency is an obvious
       problem. An optimization is an action (sometimes optional) that
       can be taken to further improve the state of the repository.

    description
       Message intended for humans explaining the improvement in more detail,
       including the implications of it. For ``deficiency`` types, should be
       worded in the present tense. For ``optimisation`` types, should be
       worded in the future tense.

    upgrademessage
       Message intended for humans explaining what an upgrade addressing this
       issue will do. Should be worded in the future tense.
    """

    def __init__(self, name, type, description, upgrademessage):
        self.name = name
        self.type = type
        self.description = description
        self.upgrademessage = upgrademessage

    def __eq__(self, other):
        if not isinstance(other, improvement):
            # This is what python tell use to do
            return NotImplemented
        return self.name == other.name

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.name)


allformatvariant = []


def registerformatvariant(cls):
    allformatvariant.append(cls)
    return cls


class formatvariant(improvement):
    """an improvement subclass dedicated to repository format"""

    type = deficiency
    ### The following attributes should be defined for each class:

    # machine-readable string uniquely identifying this improvement. it will be
    # mapped to an action later in the upgrade process.
    name = None

    # message intended for humans explaining the improvement in more detail,
    # including the implications of it ``deficiency`` types, should be worded
    # in the present tense.
    description = None

    # message intended for humans explaining what an upgrade addressing this
    # issue will do. should be worded in the future tense.
    upgrademessage = None

    # value of current Mercurial default for new repository
    default = None

    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def fromrepo(repo):
        """current value of the variant in the repository"""
        raise NotImplementedError()

    @staticmethod
    def fromconfig(repo):
        """current value of the variant in the configuration"""
        raise NotImplementedError()


class requirementformatvariant(formatvariant):
    """formatvariant based on a 'requirement' name.

    Many format variant are controlled by a 'requirement'. We define a small
    subclass to factor the code.
    """

    # the requirement that control this format variant
    _requirement = None

    @staticmethod
    def _newreporequirements(ui):
        return localrepo.newreporequirements(
            ui, localrepo.defaultcreateopts(ui)
        )

    @classmethod
    def fromrepo(cls, repo):
        assert cls._requirement is not None
        return cls._requirement in repo.requirements

    @classmethod
    def fromconfig(cls, repo):
        assert cls._requirement is not None
        return cls._requirement in cls._newreporequirements(repo.ui)


@registerformatvariant
class fncache(requirementformatvariant):
    name = b'fncache'

    _requirement = b'fncache'

    default = True

    description = _(
        b'long and reserved filenames may not work correctly; '
        b'repository performance is sub-optimal'
    )

    upgrademessage = _(
        b'repository will be more resilient to storing '
        b'certain paths and performance of certain '
        b'operations should be improved'
    )


@registerformatvariant
class dotencode(requirementformatvariant):
    name = b'dotencode'

    _requirement = b'dotencode'

    default = True

    description = _(
        b'storage of filenames beginning with a period or '
        b'space may not work correctly'
    )

    upgrademessage = _(
        b'repository will be better able to store files '
        b'beginning with a space or period'
    )


@registerformatvariant
class generaldelta(requirementformatvariant):
    name = b'generaldelta'

    _requirement = b'generaldelta'

    default = True

    description = _(
        b'deltas within internal storage are unable to '
        b'choose optimal revisions; repository is larger and '
        b'slower than it could be; interaction with other '
        b'repositories may require extra network and CPU '
        b'resources, making "hg push" and "hg pull" slower'
    )

    upgrademessage = _(
        b'repository storage will be able to create '
        b'optimal deltas; new repository data will be '
        b'smaller and read times should decrease; '
        b'interacting with other repositories using this '
        b'storage model should require less network and '
        b'CPU resources, making "hg push" and "hg pull" '
        b'faster'
    )


@registerformatvariant
class sparserevlog(requirementformatvariant):
    name = b'sparserevlog'

    _requirement = localrepo.SPARSEREVLOG_REQUIREMENT

    default = True

    description = _(
        b'in order to limit disk reading and memory usage on older '
        b'version, the span of a delta chain from its root to its '
        b'end is limited, whatever the relevant data in this span. '
        b'This can severly limit Mercurial ability to build good '
        b'chain of delta resulting is much more storage space being '
        b'taken and limit reusability of on disk delta during '
        b'exchange.'
    )

    upgrademessage = _(
        b'Revlog supports delta chain with more unused data '
        b'between payload. These gaps will be skipped at read '
        b'time. This allows for better delta chains, making a '
        b'better compression and faster exchange with server.'
    )


@registerformatvariant
class sidedata(requirementformatvariant):
    name = b'sidedata'

    _requirement = localrepo.SIDEDATA_REQUIREMENT

    default = False

    description = _(
        b'Allows storage of extra data alongside a revision, '
        b'unlocking various caching options.'
    )

    upgrademessage = _(b'Allows storage of extra data alongside a revision.')


@registerformatvariant
class copiessdc(requirementformatvariant):
    name = b'copies-sdc'

    _requirement = localrepo.COPIESSDC_REQUIREMENT

    default = False

    description = _(b'Stores copies information alongside changesets.')

    upgrademessage = _(
        b'Allows to use more efficient algorithm to deal with ' b'copy tracing.'
    )


@registerformatvariant
class removecldeltachain(formatvariant):
    name = b'plain-cl-delta'

    default = True

    description = _(
        b'changelog storage is using deltas instead of '
        b'raw entries; changelog reading and any '
        b'operation relying on changelog data are slower '
        b'than they could be'
    )

    upgrademessage = _(
        b'changelog storage will be reformated to '
        b'store raw entries; changelog reading will be '
        b'faster; changelog size may be reduced'
    )

    @staticmethod
    def fromrepo(repo):
        # Mercurial 4.0 changed changelogs to not use delta chains. Search for
        # changelogs with deltas.
        cl = repo.changelog
        chainbase = cl.chainbase
        return all(rev == chainbase(rev) for rev in cl)

    @staticmethod
    def fromconfig(repo):
        return True


@registerformatvariant
class compressionengine(formatvariant):
    name = b'compression'
    default = b'zlib'

    description = _(
        b'Compresion algorithm used to compress data. '
        b'Some engine are faster than other'
    )

    upgrademessage = _(
        b'revlog content will be recompressed with the new algorithm.'
    )

    @classmethod
    def fromrepo(cls, repo):
        # we allow multiple compression engine requirement to co-exist because
        # strickly speaking, revlog seems to support mixed compression style.
        #
        # The compression used for new entries will be "the last one"
        compression = b'zlib'
        for req in repo.requirements:
            prefix = req.startswith
            if prefix(b'revlog-compression-') or prefix(b'exp-compression-'):
                compression = req.split(b'-', 2)[2]
        return compression

    @classmethod
    def fromconfig(cls, repo):
        return repo.ui.config(b'format', b'revlog-compression')


@registerformatvariant
class compressionlevel(formatvariant):
    name = b'compression-level'
    default = b'default'

    description = _(b'compression level')

    upgrademessage = _(b'revlog content will be recompressed')

    @classmethod
    def fromrepo(cls, repo):
        comp = compressionengine.fromrepo(repo)
        level = None
        if comp == b'zlib':
            level = repo.ui.configint(b'storage', b'revlog.zlib.level')
        elif comp == b'zstd':
            level = repo.ui.configint(b'storage', b'revlog.zstd.level')
        if level is None:
            return b'default'
        return bytes(level)

    @classmethod
    def fromconfig(cls, repo):
        comp = compressionengine.fromconfig(repo)
        level = None
        if comp == b'zlib':
            level = repo.ui.configint(b'storage', b'revlog.zlib.level')
        elif comp == b'zstd':
            level = repo.ui.configint(b'storage', b'revlog.zstd.level')
        if level is None:
            return b'default'
        return bytes(level)


def finddeficiencies(repo):
    """returns a list of deficiencies that the repo suffer from"""
    deficiencies = []

    # We could detect lack of revlogv1 and store here, but they were added
    # in 0.9.2 and we don't support upgrading repos without these
    # requirements, so let's not bother.

    for fv in allformatvariant:
        if not fv.fromrepo(repo):
            deficiencies.append(fv)

    return deficiencies


# search without '-' to support older form on newer client.
#
# We don't enforce backward compatibility for debug command so this
# might eventually be dropped. However, having to use two different
# forms in script when comparing result is anoying enough to add
# backward compatibility for a while.
legacy_opts_map = {
    b'redeltaparent': b're-delta-parent',
    b'redeltamultibase': b're-delta-multibase',
    b'redeltaall': b're-delta-all',
    b'redeltafulladd': b're-delta-fulladd',
}


def findoptimizations(repo):
    """Determine optimisation that could be used during upgrade"""
    # These are unconditionally added. There is logic later that figures out
    # which ones to apply.
    optimizations = []

    optimizations.append(
        improvement(
            name=b're-delta-parent',
            type=optimisation,
            description=_(
                b'deltas within internal storage will be recalculated to '
                b'choose an optimal base revision where this was not '
                b'already done; the size of the repository may shrink and '
                b'various operations may become faster; the first time '
                b'this optimization is performed could slow down upgrade '
                b'execution considerably; subsequent invocations should '
                b'not run noticeably slower'
            ),
            upgrademessage=_(
                b'deltas within internal storage will choose a new '
                b'base revision if needed'
            ),
        )
    )

    optimizations.append(
        improvement(
            name=b're-delta-multibase',
            type=optimisation,
            description=_(
                b'deltas within internal storage will be recalculated '
                b'against multiple base revision and the smallest '
                b'difference will be used; the size of the repository may '
                b'shrink significantly when there are many merges; this '
                b'optimization will slow down execution in proportion to '
                b'the number of merges in the repository and the amount '
                b'of files in the repository; this slow down should not '
                b'be significant unless there are tens of thousands of '
                b'files and thousands of merges'
            ),
            upgrademessage=_(
                b'deltas within internal storage will choose an '
                b'optimal delta by computing deltas against multiple '
                b'parents; may slow down execution time '
                b'significantly'
            ),
        )
    )

    optimizations.append(
        improvement(
            name=b're-delta-all',
            type=optimisation,
            description=_(
                b'deltas within internal storage will always be '
                b'recalculated without reusing prior deltas; this will '
                b'likely make execution run several times slower; this '
                b'optimization is typically not needed'
            ),
            upgrademessage=_(
                b'deltas within internal storage will be fully '
                b'recomputed; this will likely drastically slow down '
                b'execution time'
            ),
        )
    )

    optimizations.append(
        improvement(
            name=b're-delta-fulladd',
            type=optimisation,
            description=_(
                b'every revision will be re-added as if it was new '
                b'content. It will go through the full storage '
                b'mechanism giving extensions a chance to process it '
                b'(eg. lfs). This is similar to "re-delta-all" but even '
                b'slower since more logic is involved.'
            ),
            upgrademessage=_(
                b'each revision will be added as new content to the '
                b'internal storage; this will likely drastically slow '
                b'down execution time, but some extensions might need '
                b'it'
            ),
        )
    )

    return optimizations


def determineactions(repo, deficiencies, sourcereqs, destreqs):
    """Determine upgrade actions that will be performed.

    Given a list of improvements as returned by ``finddeficiencies`` and
    ``findoptimizations``, determine the list of upgrade actions that
    will be performed.

    The role of this function is to filter improvements if needed, apply
    recommended optimizations from the improvements list that make sense,
    etc.

    Returns a list of action names.
    """
    newactions = []

    knownreqs = supporteddestrequirements(repo)

    for d in deficiencies:
        name = d.name

        # If the action is a requirement that doesn't show up in the
        # destination requirements, prune the action.
        if name in knownreqs and name not in destreqs:
            continue

        newactions.append(d)

    # FUTURE consider adding some optimizations here for certain transitions.
    # e.g. adding generaldelta could schedule parent redeltas.

    return newactions


def _revlogfrompath(repo, path):
    """Obtain a revlog from a repo path.

    An instance of the appropriate class is returned.
    """
    if path == b'00changelog.i':
        return changelog.changelog(repo.svfs)
    elif path.endswith(b'00manifest.i'):
        mandir = path[: -len(b'00manifest.i')]
        return manifest.manifestrevlog(repo.svfs, tree=mandir)
    else:
        # reverse of "/".join(("data", path + ".i"))
        return filelog.filelog(repo.svfs, path[5:-2])


def _copyrevlog(tr, destrepo, oldrl, unencodedname):
    """copy all relevant files for `oldrl` into `destrepo` store

    Files are copied "as is" without any transformation. The copy is performed
    without extra checks. Callers are responsible for making sure the copied
    content is compatible with format of the destination repository.
    """
    oldrl = getattr(oldrl, '_revlog', oldrl)
    newrl = _revlogfrompath(destrepo, unencodedname)
    newrl = getattr(newrl, '_revlog', newrl)

    oldvfs = oldrl.opener
    newvfs = newrl.opener
    oldindex = oldvfs.join(oldrl.indexfile)
    newindex = newvfs.join(newrl.indexfile)
    olddata = oldvfs.join(oldrl.datafile)
    newdata = newvfs.join(newrl.datafile)

    with newvfs(newrl.indexfile, b'w'):
        pass  # create all the directories

    util.copyfile(oldindex, newindex)
    copydata = oldrl.opener.exists(oldrl.datafile)
    if copydata:
        util.copyfile(olddata, newdata)

    if not (
        unencodedname.endswith(b'00changelog.i')
        or unencodedname.endswith(b'00manifest.i')
    ):
        destrepo.svfs.fncache.add(unencodedname)
        if copydata:
            destrepo.svfs.fncache.add(unencodedname[:-2] + b'.d')


UPGRADE_CHANGELOG = object()
UPGRADE_MANIFEST = object()
UPGRADE_FILELOG = object()

UPGRADE_ALL_REVLOGS = frozenset(
    [UPGRADE_CHANGELOG, UPGRADE_MANIFEST, UPGRADE_FILELOG]
)


def getsidedatacompanion(srcrepo, dstrepo):
    sidedatacompanion = None
    removedreqs = srcrepo.requirements - dstrepo.requirements
    addedreqs = dstrepo.requirements - srcrepo.requirements
    if localrepo.SIDEDATA_REQUIREMENT in removedreqs:

        def sidedatacompanion(rl, rev):
            rl = getattr(rl, '_revlog', rl)
            if rl.flags(rev) & revlog.REVIDX_SIDEDATA:
                return True, (), {}
            return False, (), {}

    elif localrepo.COPIESSDC_REQUIREMENT in addedreqs:
        sidedatacompanion = copies.getsidedataadder(srcrepo, dstrepo)
    elif localrepo.COPIESSDC_REQUIREMENT in removedreqs:
        sidedatacompanion = copies.getsidedataremover(srcrepo, dstrepo)
    return sidedatacompanion


def matchrevlog(revlogfilter, entry):
    """check is a revlog is selected for cloning

    The store entry is checked against the passed filter"""
    if entry.endswith(b'00changelog.i'):
        return UPGRADE_CHANGELOG in revlogfilter
    elif entry.endswith(b'00manifest.i'):
        return UPGRADE_MANIFEST in revlogfilter
    return UPGRADE_FILELOG in revlogfilter


def _clonerevlogs(
    ui,
    srcrepo,
    dstrepo,
    tr,
    deltareuse,
    forcedeltabothparents,
    revlogs=UPGRADE_ALL_REVLOGS,
):
    """Copy revlogs between 2 repos."""
    revcount = 0
    srcsize = 0
    srcrawsize = 0
    dstsize = 0
    fcount = 0
    frevcount = 0
    fsrcsize = 0
    frawsize = 0
    fdstsize = 0
    mcount = 0
    mrevcount = 0
    msrcsize = 0
    mrawsize = 0
    mdstsize = 0
    crevcount = 0
    csrcsize = 0
    crawsize = 0
    cdstsize = 0

    alldatafiles = list(srcrepo.store.walk())

    # Perform a pass to collect metadata. This validates we can open all
    # source files and allows a unified progress bar to be displayed.
    for unencoded, encoded, size in alldatafiles:
        if unencoded.endswith(b'.d'):
            continue

        rl = _revlogfrompath(srcrepo, unencoded)

        info = rl.storageinfo(
            exclusivefiles=True,
            revisionscount=True,
            trackedsize=True,
            storedsize=True,
        )

        revcount += info[b'revisionscount'] or 0
        datasize = info[b'storedsize'] or 0
        rawsize = info[b'trackedsize'] or 0

        srcsize += datasize
        srcrawsize += rawsize

        # This is for the separate progress bars.
        if isinstance(rl, changelog.changelog):
            crevcount += len(rl)
            csrcsize += datasize
            crawsize += rawsize
        elif isinstance(rl, manifest.manifestrevlog):
            mcount += 1
            mrevcount += len(rl)
            msrcsize += datasize
            mrawsize += rawsize
        elif isinstance(rl, filelog.filelog):
            fcount += 1
            frevcount += len(rl)
            fsrcsize += datasize
            frawsize += rawsize
        else:
            error.ProgrammingError(b'unknown revlog type')

    if not revcount:
        return

    ui.write(
        _(
            b'migrating %d total revisions (%d in filelogs, %d in manifests, '
            b'%d in changelog)\n'
        )
        % (revcount, frevcount, mrevcount, crevcount)
    )
    ui.write(
        _(b'migrating %s in store; %s tracked data\n')
        % ((util.bytecount(srcsize), util.bytecount(srcrawsize)))
    )

    # Used to keep track of progress.
    progress = None

    def oncopiedrevision(rl, rev, node):
        progress.increment()

    sidedatacompanion = getsidedatacompanion(srcrepo, dstrepo)

    # Do the actual copying.
    # FUTURE this operation can be farmed off to worker processes.
    seen = set()
    for unencoded, encoded, size in alldatafiles:
        if unencoded.endswith(b'.d'):
            continue

        oldrl = _revlogfrompath(srcrepo, unencoded)

        if isinstance(oldrl, changelog.changelog) and b'c' not in seen:
            ui.write(
                _(
                    b'finished migrating %d manifest revisions across %d '
                    b'manifests; change in size: %s\n'
                )
                % (mrevcount, mcount, util.bytecount(mdstsize - msrcsize))
            )

            ui.write(
                _(
                    b'migrating changelog containing %d revisions '
                    b'(%s in store; %s tracked data)\n'
                )
                % (
                    crevcount,
                    util.bytecount(csrcsize),
                    util.bytecount(crawsize),
                )
            )
            seen.add(b'c')
            progress = srcrepo.ui.makeprogress(
                _(b'changelog revisions'), total=crevcount
            )
        elif isinstance(oldrl, manifest.manifestrevlog) and b'm' not in seen:
            ui.write(
                _(
                    b'finished migrating %d filelog revisions across %d '
                    b'filelogs; change in size: %s\n'
                )
                % (frevcount, fcount, util.bytecount(fdstsize - fsrcsize))
            )

            ui.write(
                _(
                    b'migrating %d manifests containing %d revisions '
                    b'(%s in store; %s tracked data)\n'
                )
                % (
                    mcount,
                    mrevcount,
                    util.bytecount(msrcsize),
                    util.bytecount(mrawsize),
                )
            )
            seen.add(b'm')
            if progress:
                progress.complete()
            progress = srcrepo.ui.makeprogress(
                _(b'manifest revisions'), total=mrevcount
            )
        elif b'f' not in seen:
            ui.write(
                _(
                    b'migrating %d filelogs containing %d revisions '
                    b'(%s in store; %s tracked data)\n'
                )
                % (
                    fcount,
                    frevcount,
                    util.bytecount(fsrcsize),
                    util.bytecount(frawsize),
                )
            )
            seen.add(b'f')
            if progress:
                progress.complete()
            progress = srcrepo.ui.makeprogress(
                _(b'file revisions'), total=frevcount
            )

        if matchrevlog(revlogs, unencoded):
            ui.note(
                _(b'cloning %d revisions from %s\n') % (len(oldrl), unencoded)
            )
            newrl = _revlogfrompath(dstrepo, unencoded)
            oldrl.clone(
                tr,
                newrl,
                addrevisioncb=oncopiedrevision,
                deltareuse=deltareuse,
                forcedeltabothparents=forcedeltabothparents,
                sidedatacompanion=sidedatacompanion,
            )
        else:
            msg = _(b'blindly copying %s containing %i revisions\n')
            ui.note(msg % (unencoded, len(oldrl)))
            _copyrevlog(tr, dstrepo, oldrl, unencoded)

            newrl = _revlogfrompath(dstrepo, unencoded)

        info = newrl.storageinfo(storedsize=True)
        datasize = info[b'storedsize'] or 0

        dstsize += datasize

        if isinstance(newrl, changelog.changelog):
            cdstsize += datasize
        elif isinstance(newrl, manifest.manifestrevlog):
            mdstsize += datasize
        else:
            fdstsize += datasize

    progress.complete()

    ui.write(
        _(
            b'finished migrating %d changelog revisions; change in size: '
            b'%s\n'
        )
        % (crevcount, util.bytecount(cdstsize - csrcsize))
    )

    ui.write(
        _(
            b'finished migrating %d total revisions; total change in store '
            b'size: %s\n'
        )
        % (revcount, util.bytecount(dstsize - srcsize))
    )


def _filterstorefile(srcrepo, dstrepo, requirements, path, mode, st):
    """Determine whether to copy a store file during upgrade.

    This function is called when migrating store files from ``srcrepo`` to
    ``dstrepo`` as part of upgrading a repository.

    Args:
      srcrepo: repo we are copying from
      dstrepo: repo we are copying to
      requirements: set of requirements for ``dstrepo``
      path: store file being examined
      mode: the ``ST_MODE`` file type of ``path``
      st: ``stat`` data structure for ``path``

    Function should return ``True`` if the file is to be copied.
    """
    # Skip revlogs.
    if path.endswith((b'.i', b'.d')):
        return False
    # Skip transaction related files.
    if path.startswith(b'undo'):
        return False
    # Only copy regular files.
    if mode != stat.S_IFREG:
        return False
    # Skip other skipped files.
    if path in (b'lock', b'fncache'):
        return False

    return True


def _finishdatamigration(ui, srcrepo, dstrepo, requirements):
    """Hook point for extensions to perform additional actions during upgrade.

    This function is called after revlogs and store files have been copied but
    before the new store is swapped into the original location.
    """


def _upgraderepo(
    ui, srcrepo, dstrepo, requirements, actions, revlogs=UPGRADE_ALL_REVLOGS
):
    """Do the low-level work of upgrading a repository.

    The upgrade is effectively performed as a copy between a source
    repository and a temporary destination repository.

    The source repository is unmodified for as long as possible so the
    upgrade can abort at any time without causing loss of service for
    readers and without corrupting the source repository.
    """
    assert srcrepo.currentwlock()
    assert dstrepo.currentwlock()

    ui.write(
        _(
            b'(it is safe to interrupt this process any time before '
            b'data migration completes)\n'
        )
    )

    if b're-delta-all' in actions:
        deltareuse = revlog.revlog.DELTAREUSENEVER
    elif b're-delta-parent' in actions:
        deltareuse = revlog.revlog.DELTAREUSESAMEREVS
    elif b're-delta-multibase' in actions:
        deltareuse = revlog.revlog.DELTAREUSESAMEREVS
    elif b're-delta-fulladd' in actions:
        deltareuse = revlog.revlog.DELTAREUSEFULLADD
    else:
        deltareuse = revlog.revlog.DELTAREUSEALWAYS

    with dstrepo.transaction(b'upgrade') as tr:
        _clonerevlogs(
            ui,
            srcrepo,
            dstrepo,
            tr,
            deltareuse,
            b're-delta-multibase' in actions,
            revlogs=revlogs,
        )

    # Now copy other files in the store directory.
    # The sorted() makes execution deterministic.
    for p, kind, st in sorted(srcrepo.store.vfs.readdir(b'', stat=True)):
        if not _filterstorefile(srcrepo, dstrepo, requirements, p, kind, st):
            continue

        srcrepo.ui.write(_(b'copying %s\n') % p)
        src = srcrepo.store.rawvfs.join(p)
        dst = dstrepo.store.rawvfs.join(p)
        util.copyfile(src, dst, copystat=True)

    _finishdatamigration(ui, srcrepo, dstrepo, requirements)

    ui.write(_(b'data fully migrated to temporary repository\n'))

    backuppath = pycompat.mkdtemp(prefix=b'upgradebackup.', dir=srcrepo.path)
    backupvfs = vfsmod.vfs(backuppath)

    # Make a backup of requires file first, as it is the first to be modified.
    util.copyfile(srcrepo.vfs.join(b'requires'), backupvfs.join(b'requires'))

    # We install an arbitrary requirement that clients must not support
    # as a mechanism to lock out new clients during the data swap. This is
    # better than allowing a client to continue while the repository is in
    # an inconsistent state.
    ui.write(
        _(
            b'marking source repository as being upgraded; clients will be '
            b'unable to read from repository\n'
        )
    )
    scmutil.writerequires(
        srcrepo.vfs, srcrepo.requirements | {b'upgradeinprogress'}
    )

    ui.write(_(b'starting in-place swap of repository data\n'))
    ui.write(_(b'replaced files will be backed up at %s\n') % backuppath)

    # Now swap in the new store directory. Doing it as a rename should make
    # the operation nearly instantaneous and atomic (at least in well-behaved
    # environments).
    ui.write(_(b'replacing store...\n'))
    tstart = util.timer()
    util.rename(srcrepo.spath, backupvfs.join(b'store'))
    util.rename(dstrepo.spath, srcrepo.spath)
    elapsed = util.timer() - tstart
    ui.write(
        _(
            b'store replacement complete; repository was inconsistent for '
            b'%0.1fs\n'
        )
        % elapsed
    )

    # We first write the requirements file. Any new requirements will lock
    # out legacy clients.
    ui.write(
        _(
            b'finalizing requirements file and making repository readable '
            b'again\n'
        )
    )
    scmutil.writerequires(srcrepo.vfs, requirements)

    # The lock file from the old store won't be removed because nothing has a
    # reference to its new location. So clean it up manually. Alternatively, we
    # could update srcrepo.svfs and other variables to point to the new
    # location. This is simpler.
    backupvfs.unlink(b'store/lock')

    return backuppath


def upgraderepo(
    ui,
    repo,
    run=False,
    optimize=None,
    backup=True,
    manifest=None,
    changelog=None,
):
    """Upgrade a repository in place."""
    if optimize is None:
        optimize = []
    optimize = set(legacy_opts_map.get(o, o) for o in optimize)
    repo = repo.unfiltered()

    revlogs = set(UPGRADE_ALL_REVLOGS)
    specentries = ((b'c', changelog), (b'm', manifest))
    specified = [(y, x) for (y, x) in specentries if x is not None]
    if specified:
        # we have some limitation on revlogs to be recloned
        if any(x for y, x in specified):
            revlogs = set()
            for r, enabled in specified:
                if enabled:
                    if r == b'c':
                        revlogs.add(UPGRADE_CHANGELOG)
                    elif r == b'm':
                        revlogs.add(UPGRADE_MANIFEST)
        else:
            # none are enabled
            for r, __ in specified:
                if r == b'c':
                    revlogs.discard(UPGRADE_CHANGELOG)
                elif r == b'm':
                    revlogs.discard(UPGRADE_MANIFEST)

    # Ensure the repository can be upgraded.
    missingreqs = requiredsourcerequirements(repo) - repo.requirements
    if missingreqs:
        raise error.Abort(
            _(b'cannot upgrade repository; requirement missing: %s')
            % _(b', ').join(sorted(missingreqs))
        )

    blockedreqs = blocksourcerequirements(repo) & repo.requirements
    if blockedreqs:
        raise error.Abort(
            _(
                b'cannot upgrade repository; unsupported source '
                b'requirement: %s'
            )
            % _(b', ').join(sorted(blockedreqs))
        )

    # FUTURE there is potentially a need to control the wanted requirements via
    # command arguments or via an extension hook point.
    newreqs = localrepo.newreporequirements(
        repo.ui, localrepo.defaultcreateopts(repo.ui)
    )
    newreqs.update(preservedrequirements(repo))

    noremovereqs = (
        repo.requirements - newreqs - supportremovedrequirements(repo)
    )
    if noremovereqs:
        raise error.Abort(
            _(
                b'cannot upgrade repository; requirement would be '
                b'removed: %s'
            )
            % _(b', ').join(sorted(noremovereqs))
        )

    noaddreqs = newreqs - repo.requirements - allowednewrequirements(repo)
    if noaddreqs:
        raise error.Abort(
            _(
                b'cannot upgrade repository; do not support adding '
                b'requirement: %s'
            )
            % _(b', ').join(sorted(noaddreqs))
        )

    unsupportedreqs = newreqs - supporteddestrequirements(repo)
    if unsupportedreqs:
        raise error.Abort(
            _(
                b'cannot upgrade repository; do not support '
                b'destination requirement: %s'
            )
            % _(b', ').join(sorted(unsupportedreqs))
        )

    # Find and validate all improvements that can be made.
    alloptimizations = findoptimizations(repo)

    # Apply and Validate arguments.
    optimizations = []
    for o in alloptimizations:
        if o.name in optimize:
            optimizations.append(o)
            optimize.discard(o.name)

    if optimize:  # anything left is unknown
        raise error.Abort(
            _(b'unknown optimization action requested: %s')
            % b', '.join(sorted(optimize)),
            hint=_(b'run without arguments to see valid optimizations'),
        )

    deficiencies = finddeficiencies(repo)
    actions = determineactions(repo, deficiencies, repo.requirements, newreqs)
    actions.extend(
        o
        for o in sorted(optimizations)
        # determineactions could have added optimisation
        if o not in actions
    )

    removedreqs = repo.requirements - newreqs
    addedreqs = newreqs - repo.requirements

    if revlogs != UPGRADE_ALL_REVLOGS:
        incompatible = RECLONES_REQUIREMENTS & (removedreqs | addedreqs)
        if incompatible:
            msg = _(
                b'ignoring revlogs selection flags, format requirements '
                b'change: %s\n'
            )
            ui.warn(msg % b', '.join(sorted(incompatible)))
            revlogs = UPGRADE_ALL_REVLOGS

    def write_labeled(l, label):
        first = True
        for r in sorted(l):
            if not first:
                ui.write(b', ')
            ui.write(r, label=label)
            first = False

    def printrequirements():
        ui.write(_(b'requirements\n'))
        ui.write(_(b'   preserved: '))
        write_labeled(
            newreqs & repo.requirements, "upgrade-repo.requirement.preserved"
        )
        ui.write((b'\n'))
        removed = repo.requirements - newreqs
        if repo.requirements - newreqs:
            ui.write(_(b'   removed: '))
            write_labeled(removed, "upgrade-repo.requirement.removed")
            ui.write((b'\n'))
        added = newreqs - repo.requirements
        if added:
            ui.write(_(b'   added: '))
            write_labeled(added, "upgrade-repo.requirement.added")
            ui.write((b'\n'))
        ui.write(b'\n')

    def printupgradeactions():
        for a in actions:
            ui.write(b'%s\n   %s\n\n' % (a.name, a.upgrademessage))

    if not run:
        fromconfig = []
        onlydefault = []

        for d in deficiencies:
            if d.fromconfig(repo):
                fromconfig.append(d)
            elif d.default:
                onlydefault.append(d)

        if fromconfig or onlydefault:

            if fromconfig:
                ui.write(
                    _(
                        b'repository lacks features recommended by '
                        b'current config options:\n\n'
                    )
                )
                for i in fromconfig:
                    ui.write(b'%s\n   %s\n\n' % (i.name, i.description))

            if onlydefault:
                ui.write(
                    _(
                        b'repository lacks features used by the default '
                        b'config options:\n\n'
                    )
                )
                for i in onlydefault:
                    ui.write(b'%s\n   %s\n\n' % (i.name, i.description))

            ui.write(b'\n')
        else:
            ui.write(
                _(
                    b'(no feature deficiencies found in existing '
                    b'repository)\n'
                )
            )

        ui.write(
            _(
                b'performing an upgrade with "--run" will make the following '
                b'changes:\n\n'
            )
        )

        printrequirements()
        printupgradeactions()

        unusedoptimize = [i for i in alloptimizations if i not in actions]

        if unusedoptimize:
            ui.write(
                _(
                    b'additional optimizations are available by specifying '
                    b'"--optimize <name>":\n\n'
                )
            )
            for i in unusedoptimize:
                ui.write(_(b'%s\n   %s\n\n') % (i.name, i.description))
        return

    # Else we're in the run=true case.
    ui.write(_(b'upgrade will perform the following actions:\n\n'))
    printrequirements()
    printupgradeactions()

    upgradeactions = [a.name for a in actions]

    ui.write(_(b'beginning upgrade...\n'))
    with repo.wlock(), repo.lock():
        ui.write(_(b'repository locked and read-only\n'))
        # Our strategy for upgrading the repository is to create a new,
        # temporary repository, write data to it, then do a swap of the
        # data. There are less heavyweight ways to do this, but it is easier
        # to create a new repo object than to instantiate all the components
        # (like the store) separately.
        tmppath = pycompat.mkdtemp(prefix=b'upgrade.', dir=repo.path)
        backuppath = None
        try:
            ui.write(
                _(
                    b'creating temporary repository to stage migrated '
                    b'data: %s\n'
                )
                % tmppath
            )

            # clone ui without using ui.copy because repo.ui is protected
            repoui = repo.ui.__class__(repo.ui)
            dstrepo = hg.repository(repoui, path=tmppath, create=True)

            with dstrepo.wlock(), dstrepo.lock():
                backuppath = _upgraderepo(
                    ui, repo, dstrepo, newreqs, upgradeactions, revlogs=revlogs
                )
            if not (backup or backuppath is None):
                ui.write(_(b'removing old repository content%s\n') % backuppath)
                repo.vfs.rmtree(backuppath, forcibly=True)
                backuppath = None

        finally:
            ui.write(_(b'removing temporary repository %s\n') % tmppath)
            repo.vfs.rmtree(tmppath, forcibly=True)

            if backuppath:
                ui.warn(
                    _(b'copy of old repository backed up at %s\n') % backuppath
                )
                ui.warn(
                    _(
                        b'the old repository will not be deleted; remove '
                        b'it to free up disk space once the upgraded '
                        b'repository is verified\n'
                    )
                )
