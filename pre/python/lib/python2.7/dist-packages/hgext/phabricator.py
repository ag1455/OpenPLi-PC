# phabricator.py - simple Phabricator integration
#
# Copyright 2017 Facebook, Inc.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""simple Phabricator integration (EXPERIMENTAL)

This extension provides a ``phabsend`` command which sends a stack of
changesets to Phabricator, and a ``phabread`` command which prints a stack of
revisions in a format suitable for :hg:`import`, and a ``phabupdate`` command
to update statuses in batch.

A "phabstatus" view for :hg:`show` is also provided; it displays status
information of Phabricator differentials associated with unfinished
changesets.

By default, Phabricator requires ``Test Plan`` which might prevent some
changeset from being sent. The requirement could be disabled by changing
``differential.require-test-plan-field`` config server side.

Config::

    [phabricator]
    # Phabricator URL
    url = https://phab.example.com/

    # Repo callsign. If a repo has a URL https://$HOST/diffusion/FOO, then its
    # callsign is "FOO".
    callsign = FOO

    # curl command to use. If not set (default), use builtin HTTP library to
    # communicate. If set, use the specified curl command. This could be useful
    # if you need to specify advanced options that is not easily supported by
    # the internal library.
    curlcmd = curl --connect-timeout 2 --retry 3 --silent

    [auth]
    example.schemes = https
    example.prefix = phab.example.com

    # API token. Get it from https://$HOST/conduit/login/
    example.phabtoken = cli-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""

from __future__ import absolute_import

import base64
import contextlib
import hashlib
import itertools
import json
import mimetypes
import operator
import re

from mercurial.node import bin, nullid
from mercurial.i18n import _
from mercurial.pycompat import getattr
from mercurial.thirdparty import attr
from mercurial import (
    cmdutil,
    context,
    encoding,
    error,
    exthelper,
    graphmod,
    httpconnection as httpconnectionmod,
    localrepo,
    logcmdutil,
    match,
    mdiff,
    obsutil,
    parser,
    patch,
    phases,
    pycompat,
    scmutil,
    smartset,
    tags,
    templatefilters,
    templateutil,
    url as urlmod,
    util,
)
from mercurial.utils import (
    procutil,
    stringutil,
)
from . import show


# Note for extension authors: ONLY specify testedwith = 'ships-with-hg-core' for
# extensions which SHIP WITH MERCURIAL. Non-mainline extensions should
# be specifying the version(s) of Mercurial they are tested with, or
# leave the attribute unspecified.
testedwith = b'ships-with-hg-core'

eh = exthelper.exthelper()

cmdtable = eh.cmdtable
command = eh.command
configtable = eh.configtable
templatekeyword = eh.templatekeyword
uisetup = eh.finaluisetup

# developer config: phabricator.batchsize
eh.configitem(
    b'phabricator', b'batchsize', default=12,
)
eh.configitem(
    b'phabricator', b'callsign', default=None,
)
eh.configitem(
    b'phabricator', b'curlcmd', default=None,
)
# developer config: phabricator.repophid
eh.configitem(
    b'phabricator', b'repophid', default=None,
)
eh.configitem(
    b'phabricator', b'url', default=None,
)
eh.configitem(
    b'phabsend', b'confirm', default=False,
)

colortable = {
    b'phabricator.action.created': b'green',
    b'phabricator.action.skipped': b'magenta',
    b'phabricator.action.updated': b'magenta',
    b'phabricator.desc': b'',
    b'phabricator.drev': b'bold',
    b'phabricator.node': b'',
    b'phabricator.status.abandoned': b'magenta dim',
    b'phabricator.status.accepted': b'green bold',
    b'phabricator.status.closed': b'green',
    b'phabricator.status.needsreview': b'yellow',
    b'phabricator.status.needsrevision': b'red',
    b'phabricator.status.changesplanned': b'red',
}

_VCR_FLAGS = [
    (
        b'',
        b'test-vcr',
        b'',
        _(
            b'Path to a vcr file. If nonexistent, will record a new vcr transcript'
            b', otherwise will mock all http requests using the specified vcr file.'
            b' (ADVANCED)'
        ),
    ),
]


@eh.wrapfunction(localrepo, "loadhgrc")
def _loadhgrc(orig, ui, wdirvfs, hgvfs, requirements):
    """Load ``.arcconfig`` content into a ui instance on repository open.
    """
    result = False
    arcconfig = {}

    try:
        # json.loads only accepts bytes from 3.6+
        rawparams = encoding.unifromlocal(wdirvfs.read(b".arcconfig"))
        # json.loads only returns unicode strings
        arcconfig = pycompat.rapply(
            lambda x: encoding.unitolocal(x)
            if isinstance(x, pycompat.unicode)
            else x,
            pycompat.json_loads(rawparams),
        )

        result = True
    except ValueError:
        ui.warn(_(b"invalid JSON in %s\n") % wdirvfs.join(b".arcconfig"))
    except IOError:
        pass

    cfg = util.sortdict()

    if b"repository.callsign" in arcconfig:
        cfg[(b"phabricator", b"callsign")] = arcconfig[b"repository.callsign"]

    if b"phabricator.uri" in arcconfig:
        cfg[(b"phabricator", b"url")] = arcconfig[b"phabricator.uri"]

    if cfg:
        ui.applyconfig(cfg, source=wdirvfs.join(b".arcconfig"))

    return orig(ui, wdirvfs, hgvfs, requirements) or result  # Load .hg/hgrc


def vcrcommand(name, flags, spec, helpcategory=None, optionalrepo=False):
    fullflags = flags + _VCR_FLAGS

    def hgmatcher(r1, r2):
        if r1.uri != r2.uri or r1.method != r2.method:
            return False
        r1params = util.urlreq.parseqs(r1.body)
        r2params = util.urlreq.parseqs(r2.body)
        for key in r1params:
            if key not in r2params:
                return False
            value = r1params[key][0]
            # we want to compare json payloads without worrying about ordering
            if value.startswith(b'{') and value.endswith(b'}'):
                r1json = pycompat.json_loads(value)
                r2json = pycompat.json_loads(r2params[key][0])
                if r1json != r2json:
                    return False
            elif r2params[key][0] != value:
                return False
        return True

    def sanitiserequest(request):
        request.body = re.sub(
            br'cli-[a-z0-9]+', br'cli-hahayouwish', request.body
        )
        return request

    def sanitiseresponse(response):
        if 'set-cookie' in response['headers']:
            del response['headers']['set-cookie']
        return response

    def decorate(fn):
        def inner(*args, **kwargs):
            cassette = pycompat.fsdecode(kwargs.pop('test_vcr', None))
            if cassette:
                import hgdemandimport

                with hgdemandimport.deactivated():
                    import vcr as vcrmod
                    import vcr.stubs as stubs

                    vcr = vcrmod.VCR(
                        serializer='json',
                        before_record_request=sanitiserequest,
                        before_record_response=sanitiseresponse,
                        custom_patches=[
                            (
                                urlmod,
                                'httpconnection',
                                stubs.VCRHTTPConnection,
                            ),
                            (
                                urlmod,
                                'httpsconnection',
                                stubs.VCRHTTPSConnection,
                            ),
                        ],
                    )
                    vcr.register_matcher('hgmatcher', hgmatcher)
                    with vcr.use_cassette(cassette, match_on=['hgmatcher']):
                        return fn(*args, **kwargs)
            return fn(*args, **kwargs)

        inner.__name__ = fn.__name__
        inner.__doc__ = fn.__doc__
        return command(
            name,
            fullflags,
            spec,
            helpcategory=helpcategory,
            optionalrepo=optionalrepo,
        )(inner)

    return decorate


def urlencodenested(params):
    """like urlencode, but works with nested parameters.

    For example, if params is {'a': ['b', 'c'], 'd': {'e': 'f'}}, it will be
    flattened to {'a[0]': 'b', 'a[1]': 'c', 'd[e]': 'f'} and then passed to
    urlencode. Note: the encoding is consistent with PHP's http_build_query.
    """
    flatparams = util.sortdict()

    def process(prefix, obj):
        if isinstance(obj, bool):
            obj = {True: b'true', False: b'false'}[obj]  # Python -> PHP form
        lister = lambda l: [(b'%d' % k, v) for k, v in enumerate(l)]
        items = {list: lister, dict: lambda x: x.items()}.get(type(obj))
        if items is None:
            flatparams[prefix] = obj
        else:
            for k, v in items(obj):
                if prefix:
                    process(b'%s[%s]' % (prefix, k), v)
                else:
                    process(k, v)

    process(b'', params)
    return util.urlreq.urlencode(flatparams)


def readurltoken(ui):
    """return conduit url, token and make sure they exist

    Currently read from [auth] config section. In the future, it might
    make sense to read from .arcconfig and .arcrc as well.
    """
    url = ui.config(b'phabricator', b'url')
    if not url:
        raise error.Abort(
            _(b'config %s.%s is required') % (b'phabricator', b'url')
        )

    res = httpconnectionmod.readauthforuri(ui, url, util.url(url).user)
    token = None

    if res:
        group, auth = res

        ui.debug(b"using auth.%s.* for authentication\n" % group)

        token = auth.get(b'phabtoken')

    if not token:
        raise error.Abort(
            _(b'Can\'t find conduit token associated to %s') % (url,)
        )

    return url, token


def callconduit(ui, name, params):
    """call Conduit API, params is a dict. return json.loads result, or None"""
    host, token = readurltoken(ui)
    url, authinfo = util.url(b'/'.join([host, b'api', name])).authinfo()
    ui.debug(b'Conduit Call: %s %s\n' % (url, pycompat.byterepr(params)))
    params = params.copy()
    params[b'__conduit__'] = {
        b'token': token,
    }
    rawdata = {
        b'params': templatefilters.json(params),
        b'output': b'json',
        b'__conduit__': 1,
    }
    data = urlencodenested(rawdata)
    curlcmd = ui.config(b'phabricator', b'curlcmd')
    if curlcmd:
        sin, sout = procutil.popen2(
            b'%s -d @- %s' % (curlcmd, procutil.shellquote(url))
        )
        sin.write(data)
        sin.close()
        body = sout.read()
    else:
        urlopener = urlmod.opener(ui, authinfo)
        request = util.urlreq.request(pycompat.strurl(url), data=data)
        with contextlib.closing(urlopener.open(request)) as rsp:
            body = rsp.read()
    ui.debug(b'Conduit Response: %s\n' % body)
    parsed = pycompat.rapply(
        lambda x: encoding.unitolocal(x)
        if isinstance(x, pycompat.unicode)
        else x,
        # json.loads only accepts bytes from py3.6+
        pycompat.json_loads(encoding.unifromlocal(body)),
    )
    if parsed.get(b'error_code'):
        msg = _(b'Conduit Error (%s): %s') % (
            parsed[b'error_code'],
            parsed[b'error_info'],
        )
        raise error.Abort(msg)
    return parsed[b'result']


@vcrcommand(b'debugcallconduit', [], _(b'METHOD'), optionalrepo=True)
def debugcallconduit(ui, repo, name):
    """call Conduit API

    Call parameters are read from stdin as a JSON blob. Result will be written
    to stdout as a JSON blob.
    """
    # json.loads only accepts bytes from 3.6+
    rawparams = encoding.unifromlocal(ui.fin.read())
    # json.loads only returns unicode strings
    params = pycompat.rapply(
        lambda x: encoding.unitolocal(x)
        if isinstance(x, pycompat.unicode)
        else x,
        pycompat.json_loads(rawparams),
    )
    # json.dumps only accepts unicode strings
    result = pycompat.rapply(
        lambda x: encoding.unifromlocal(x) if isinstance(x, bytes) else x,
        callconduit(ui, name, params),
    )
    s = json.dumps(result, sort_keys=True, indent=2, separators=(u',', u': '))
    ui.write(b'%s\n' % encoding.unitolocal(s))


def getrepophid(repo):
    """given callsign, return repository PHID or None"""
    # developer config: phabricator.repophid
    repophid = repo.ui.config(b'phabricator', b'repophid')
    if repophid:
        return repophid
    callsign = repo.ui.config(b'phabricator', b'callsign')
    if not callsign:
        return None
    query = callconduit(
        repo.ui,
        b'diffusion.repository.search',
        {b'constraints': {b'callsigns': [callsign]}},
    )
    if len(query[b'data']) == 0:
        return None
    repophid = query[b'data'][0][b'phid']
    repo.ui.setconfig(b'phabricator', b'repophid', repophid)
    return repophid


_differentialrevisiontagre = re.compile(br'\AD([1-9][0-9]*)\Z')
_differentialrevisiondescre = re.compile(
    br'^Differential Revision:\s*(?P<url>(?:.*)D(?P<id>[1-9][0-9]*))$', re.M
)


def getoldnodedrevmap(repo, nodelist):
    """find previous nodes that has been sent to Phabricator

    return {node: (oldnode, Differential diff, Differential Revision ID)}
    for node in nodelist with known previous sent versions, or associated
    Differential Revision IDs. ``oldnode`` and ``Differential diff`` could
    be ``None``.

    Examines commit messages like "Differential Revision:" to get the
    association information.

    If such commit message line is not found, examines all precursors and their
    tags. Tags with format like "D1234" are considered a match and the node
    with that tag, and the number after "D" (ex. 1234) will be returned.

    The ``old node``, if not None, is guaranteed to be the last diff of
    corresponding Differential Revision, and exist in the repo.
    """
    unfi = repo.unfiltered()
    has_node = unfi.changelog.index.has_node

    result = {}  # {node: (oldnode?, lastdiff?, drev)}
    toconfirm = {}  # {node: (force, {precnode}, drev)}
    for node in nodelist:
        ctx = unfi[node]
        # For tags like "D123", put them into "toconfirm" to verify later
        precnodes = list(obsutil.allpredecessors(unfi.obsstore, [node]))
        for n in precnodes:
            if has_node(n):
                for tag in unfi.nodetags(n):
                    m = _differentialrevisiontagre.match(tag)
                    if m:
                        toconfirm[node] = (0, set(precnodes), int(m.group(1)))
                        break
                else:
                    continue  # move to next predecessor
                break  # found a tag, stop
        else:
            # Check commit message
            m = _differentialrevisiondescre.search(ctx.description())
            if m:
                toconfirm[node] = (1, set(precnodes), int(m.group('id')))

    # Double check if tags are genuine by collecting all old nodes from
    # Phabricator, and expect precursors overlap with it.
    if toconfirm:
        drevs = [drev for force, precs, drev in toconfirm.values()]
        alldiffs = callconduit(
            unfi.ui, b'differential.querydiffs', {b'revisionIDs': drevs}
        )
        getnode = lambda d: bin(getdiffmeta(d).get(b'node', b'')) or None
        for newnode, (force, precset, drev) in toconfirm.items():
            diffs = [
                d for d in alldiffs.values() if int(d[b'revisionID']) == drev
            ]

            # "precursors" as known by Phabricator
            phprecset = set(getnode(d) for d in diffs)

            # Ignore if precursors (Phabricator and local repo) do not overlap,
            # and force is not set (when commit message says nothing)
            if not force and not bool(phprecset & precset):
                tagname = b'D%d' % drev
                tags.tag(
                    repo,
                    tagname,
                    nullid,
                    message=None,
                    user=None,
                    date=None,
                    local=True,
                )
                unfi.ui.warn(
                    _(
                        b'D%d: local tag removed - does not match '
                        b'Differential history\n'
                    )
                    % drev
                )
                continue

            # Find the last node using Phabricator metadata, and make sure it
            # exists in the repo
            oldnode = lastdiff = None
            if diffs:
                lastdiff = max(diffs, key=lambda d: int(d[b'id']))
                oldnode = getnode(lastdiff)
                if oldnode and not has_node(oldnode):
                    oldnode = None

            result[newnode] = (oldnode, lastdiff, drev)

    return result


def getdrevmap(repo, revs):
    """Return a dict mapping each rev in `revs` to their Differential Revision
    ID or None.
    """
    result = {}
    for rev in revs:
        result[rev] = None
        ctx = repo[rev]
        # Check commit message
        m = _differentialrevisiondescre.search(ctx.description())
        if m:
            result[rev] = int(m.group('id'))
            continue
        # Check tags
        for tag in repo.nodetags(ctx.node()):
            m = _differentialrevisiontagre.match(tag)
            if m:
                result[rev] = int(m.group(1))
                break

    return result


def getdiff(ctx, diffopts):
    """plain-text diff without header (user, commit message, etc)"""
    output = util.stringio()
    for chunk, _label in patch.diffui(
        ctx.repo(), ctx.p1().node(), ctx.node(), None, opts=diffopts
    ):
        output.write(chunk)
    return output.getvalue()


class DiffChangeType(object):
    ADD = 1
    CHANGE = 2
    DELETE = 3
    MOVE_AWAY = 4
    COPY_AWAY = 5
    MOVE_HERE = 6
    COPY_HERE = 7
    MULTICOPY = 8


class DiffFileType(object):
    TEXT = 1
    IMAGE = 2
    BINARY = 3


@attr.s
class phabhunk(dict):
    """Represents a Differential hunk, which is owned by a Differential change
    """

    oldOffset = attr.ib(default=0)  # camelcase-required
    oldLength = attr.ib(default=0)  # camelcase-required
    newOffset = attr.ib(default=0)  # camelcase-required
    newLength = attr.ib(default=0)  # camelcase-required
    corpus = attr.ib(default='')
    # These get added to the phabchange's equivalents
    addLines = attr.ib(default=0)  # camelcase-required
    delLines = attr.ib(default=0)  # camelcase-required


@attr.s
class phabchange(object):
    """Represents a Differential change, owns Differential hunks and owned by a
    Differential diff.  Each one represents one file in a diff.
    """

    currentPath = attr.ib(default=None)  # camelcase-required
    oldPath = attr.ib(default=None)  # camelcase-required
    awayPaths = attr.ib(default=attr.Factory(list))  # camelcase-required
    metadata = attr.ib(default=attr.Factory(dict))
    oldProperties = attr.ib(default=attr.Factory(dict))  # camelcase-required
    newProperties = attr.ib(default=attr.Factory(dict))  # camelcase-required
    type = attr.ib(default=DiffChangeType.CHANGE)
    fileType = attr.ib(default=DiffFileType.TEXT)  # camelcase-required
    commitHash = attr.ib(default=None)  # camelcase-required
    addLines = attr.ib(default=0)  # camelcase-required
    delLines = attr.ib(default=0)  # camelcase-required
    hunks = attr.ib(default=attr.Factory(list))

    def copynewmetadatatoold(self):
        for key in list(self.metadata.keys()):
            newkey = key.replace(b'new:', b'old:')
            self.metadata[newkey] = self.metadata[key]

    def addoldmode(self, value):
        self.oldProperties[b'unix:filemode'] = value

    def addnewmode(self, value):
        self.newProperties[b'unix:filemode'] = value

    def addhunk(self, hunk):
        if not isinstance(hunk, phabhunk):
            raise error.Abort(b'phabchange.addhunk only takes phabhunks')
        self.hunks.append(pycompat.byteskwargs(attr.asdict(hunk)))
        # It's useful to include these stats since the Phab web UI shows them,
        # and uses them to estimate how large a change a Revision is. Also used
        # in email subjects for the [+++--] bit.
        self.addLines += hunk.addLines
        self.delLines += hunk.delLines


@attr.s
class phabdiff(object):
    """Represents a Differential diff, owns Differential changes.  Corresponds
    to a commit.
    """

    # Doesn't seem to be any reason to send this (output of uname -n)
    sourceMachine = attr.ib(default=b'')  # camelcase-required
    sourcePath = attr.ib(default=b'/')  # camelcase-required
    sourceControlBaseRevision = attr.ib(default=b'0' * 40)  # camelcase-required
    sourceControlPath = attr.ib(default=b'/')  # camelcase-required
    sourceControlSystem = attr.ib(default=b'hg')  # camelcase-required
    branch = attr.ib(default=b'default')
    bookmark = attr.ib(default=None)
    creationMethod = attr.ib(default=b'phabsend')  # camelcase-required
    lintStatus = attr.ib(default=b'none')  # camelcase-required
    unitStatus = attr.ib(default=b'none')  # camelcase-required
    changes = attr.ib(default=attr.Factory(dict))
    repositoryPHID = attr.ib(default=None)  # camelcase-required

    def addchange(self, change):
        if not isinstance(change, phabchange):
            raise error.Abort(b'phabdiff.addchange only takes phabchanges')
        self.changes[change.currentPath] = pycompat.byteskwargs(
            attr.asdict(change)
        )


def maketext(pchange, ctx, fname):
    """populate the phabchange for a text file"""
    repo = ctx.repo()
    fmatcher = match.exact([fname])
    diffopts = mdiff.diffopts(git=True, context=32767)
    _pfctx, _fctx, header, fhunks = next(
        patch.diffhunks(repo, ctx.p1(), ctx, fmatcher, opts=diffopts)
    )

    for fhunk in fhunks:
        (oldOffset, oldLength, newOffset, newLength), lines = fhunk
        corpus = b''.join(lines[1:])
        shunk = list(header)
        shunk.extend(lines)
        _mf, _mt, addLines, delLines, _hb = patch.diffstatsum(
            patch.diffstatdata(util.iterlines(shunk))
        )
        pchange.addhunk(
            phabhunk(
                oldOffset,
                oldLength,
                newOffset,
                newLength,
                corpus,
                addLines,
                delLines,
            )
        )


def uploadchunks(fctx, fphid):
    """upload large binary files as separate chunks.
    Phab requests chunking over 8MiB, and splits into 4MiB chunks
    """
    ui = fctx.repo().ui
    chunks = callconduit(ui, b'file.querychunks', {b'filePHID': fphid})
    with ui.makeprogress(
        _(b'uploading file chunks'), unit=_(b'chunks'), total=len(chunks)
    ) as progress:
        for chunk in chunks:
            progress.increment()
            if chunk[b'complete']:
                continue
            bstart = int(chunk[b'byteStart'])
            bend = int(chunk[b'byteEnd'])
            callconduit(
                ui,
                b'file.uploadchunk',
                {
                    b'filePHID': fphid,
                    b'byteStart': bstart,
                    b'data': base64.b64encode(fctx.data()[bstart:bend]),
                    b'dataEncoding': b'base64',
                },
            )


def uploadfile(fctx):
    """upload binary files to Phabricator"""
    repo = fctx.repo()
    ui = repo.ui
    fname = fctx.path()
    size = fctx.size()
    fhash = pycompat.bytestr(hashlib.sha256(fctx.data()).hexdigest())

    # an allocate call is required first to see if an upload is even required
    # (Phab might already have it) and to determine if chunking is needed
    allocateparams = {
        b'name': fname,
        b'contentLength': size,
        b'contentHash': fhash,
    }
    filealloc = callconduit(ui, b'file.allocate', allocateparams)
    fphid = filealloc[b'filePHID']

    if filealloc[b'upload']:
        ui.write(_(b'uploading %s\n') % bytes(fctx))
        if not fphid:
            uploadparams = {
                b'name': fname,
                b'data_base64': base64.b64encode(fctx.data()),
            }
            fphid = callconduit(ui, b'file.upload', uploadparams)
        else:
            uploadchunks(fctx, fphid)
    else:
        ui.debug(b'server already has %s\n' % bytes(fctx))

    if not fphid:
        raise error.Abort(b'Upload of %s failed.' % bytes(fctx))

    return fphid


def addoldbinary(pchange, fctx):
    """add the metadata for the previous version of a binary file to the
    phabchange for the new version
    """
    oldfctx = fctx.p1()
    if fctx.cmp(oldfctx):
        # Files differ, add the old one
        pchange.metadata[b'old:file:size'] = oldfctx.size()
        mimeguess, _enc = mimetypes.guess_type(
            encoding.unifromlocal(oldfctx.path())
        )
        if mimeguess:
            pchange.metadata[b'old:file:mime-type'] = pycompat.bytestr(
                mimeguess
            )
        fphid = uploadfile(oldfctx)
        pchange.metadata[b'old:binary-phid'] = fphid
    else:
        # If it's left as IMAGE/BINARY web UI might try to display it
        pchange.fileType = DiffFileType.TEXT
        pchange.copynewmetadatatoold()


def makebinary(pchange, fctx):
    """populate the phabchange for a binary file"""
    pchange.fileType = DiffFileType.BINARY
    fphid = uploadfile(fctx)
    pchange.metadata[b'new:binary-phid'] = fphid
    pchange.metadata[b'new:file:size'] = fctx.size()
    mimeguess, _enc = mimetypes.guess_type(encoding.unifromlocal(fctx.path()))
    if mimeguess:
        mimeguess = pycompat.bytestr(mimeguess)
        pchange.metadata[b'new:file:mime-type'] = mimeguess
        if mimeguess.startswith(b'image/'):
            pchange.fileType = DiffFileType.IMAGE


# Copied from mercurial/patch.py
gitmode = {b'l': b'120000', b'x': b'100755', b'': b'100644'}


def notutf8(fctx):
    """detect non-UTF-8 text files since Phabricator requires them to be marked
    as binary
    """
    try:
        fctx.data().decode('utf-8')
        if fctx.parents():
            fctx.p1().data().decode('utf-8')
        return False
    except UnicodeDecodeError:
        fctx.repo().ui.write(
            _(b'file %s detected as non-UTF-8, marked as binary\n')
            % fctx.path()
        )
        return True


def addremoved(pdiff, ctx, removed):
    """add removed files to the phabdiff. Shouldn't include moves"""
    for fname in removed:
        pchange = phabchange(
            currentPath=fname, oldPath=fname, type=DiffChangeType.DELETE
        )
        pchange.addoldmode(gitmode[ctx.p1()[fname].flags()])
        fctx = ctx.p1()[fname]
        if not (fctx.isbinary() or notutf8(fctx)):
            maketext(pchange, ctx, fname)

        pdiff.addchange(pchange)


def addmodified(pdiff, ctx, modified):
    """add modified files to the phabdiff"""
    for fname in modified:
        fctx = ctx[fname]
        pchange = phabchange(currentPath=fname, oldPath=fname)
        filemode = gitmode[ctx[fname].flags()]
        originalmode = gitmode[ctx.p1()[fname].flags()]
        if filemode != originalmode:
            pchange.addoldmode(originalmode)
            pchange.addnewmode(filemode)

        if fctx.isbinary() or notutf8(fctx):
            makebinary(pchange, fctx)
            addoldbinary(pchange, fctx)
        else:
            maketext(pchange, ctx, fname)

        pdiff.addchange(pchange)


def addadded(pdiff, ctx, added, removed):
    """add file adds to the phabdiff, both new files and copies/moves"""
    # Keep track of files that've been recorded as moved/copied, so if there are
    # additional copies we can mark them (moves get removed from removed)
    copiedchanges = {}
    movedchanges = {}
    for fname in added:
        fctx = ctx[fname]
        pchange = phabchange(currentPath=fname)

        filemode = gitmode[ctx[fname].flags()]
        renamed = fctx.renamed()

        if renamed:
            originalfname = renamed[0]
            originalmode = gitmode[ctx.p1()[originalfname].flags()]
            pchange.oldPath = originalfname

            if originalfname in removed:
                origpchange = phabchange(
                    currentPath=originalfname,
                    oldPath=originalfname,
                    type=DiffChangeType.MOVE_AWAY,
                    awayPaths=[fname],
                )
                movedchanges[originalfname] = origpchange
                removed.remove(originalfname)
                pchange.type = DiffChangeType.MOVE_HERE
            elif originalfname in movedchanges:
                movedchanges[originalfname].type = DiffChangeType.MULTICOPY
                movedchanges[originalfname].awayPaths.append(fname)
                pchange.type = DiffChangeType.COPY_HERE
            else:  # pure copy
                if originalfname not in copiedchanges:
                    origpchange = phabchange(
                        currentPath=originalfname, type=DiffChangeType.COPY_AWAY
                    )
                    copiedchanges[originalfname] = origpchange
                else:
                    origpchange = copiedchanges[originalfname]
                origpchange.awayPaths.append(fname)
                pchange.type = DiffChangeType.COPY_HERE

            if filemode != originalmode:
                pchange.addoldmode(originalmode)
                pchange.addnewmode(filemode)
        else:  # Brand-new file
            pchange.addnewmode(gitmode[fctx.flags()])
            pchange.type = DiffChangeType.ADD

        if fctx.isbinary() or notutf8(fctx):
            makebinary(pchange, fctx)
            if renamed:
                addoldbinary(pchange, fctx)
        else:
            maketext(pchange, ctx, fname)

        pdiff.addchange(pchange)

    for _path, copiedchange in copiedchanges.items():
        pdiff.addchange(copiedchange)
    for _path, movedchange in movedchanges.items():
        pdiff.addchange(movedchange)


def creatediff(ctx):
    """create a Differential Diff"""
    repo = ctx.repo()
    repophid = getrepophid(repo)
    # Create a "Differential Diff" via "differential.creatediff" API
    pdiff = phabdiff(
        sourceControlBaseRevision=b'%s' % ctx.p1().hex(),
        branch=b'%s' % ctx.branch(),
    )
    modified, added, removed, _d, _u, _i, _c = ctx.p1().status(ctx)
    # addadded will remove moved files from removed, so addremoved won't get
    # them
    addadded(pdiff, ctx, added, removed)
    addmodified(pdiff, ctx, modified)
    addremoved(pdiff, ctx, removed)
    if repophid:
        pdiff.repositoryPHID = repophid
    diff = callconduit(
        repo.ui,
        b'differential.creatediff',
        pycompat.byteskwargs(attr.asdict(pdiff)),
    )
    if not diff:
        raise error.Abort(_(b'cannot create diff for %s') % ctx)
    return diff


def writediffproperties(ctx, diff):
    """write metadata to diff so patches could be applied losslessly"""
    # creatediff returns with a diffid but query returns with an id
    diffid = diff.get(b'diffid', diff.get(b'id'))
    params = {
        b'diff_id': diffid,
        b'name': b'hg:meta',
        b'data': templatefilters.json(
            {
                b'user': ctx.user(),
                b'date': b'%d %d' % ctx.date(),
                b'branch': ctx.branch(),
                b'node': ctx.hex(),
                b'parent': ctx.p1().hex(),
            }
        ),
    }
    callconduit(ctx.repo().ui, b'differential.setdiffproperty', params)

    params = {
        b'diff_id': diffid,
        b'name': b'local:commits',
        b'data': templatefilters.json(
            {
                ctx.hex(): {
                    b'author': stringutil.person(ctx.user()),
                    b'authorEmail': stringutil.email(ctx.user()),
                    b'time': int(ctx.date()[0]),
                    b'commit': ctx.hex(),
                    b'parents': [ctx.p1().hex()],
                    b'branch': ctx.branch(),
                },
            }
        ),
    }
    callconduit(ctx.repo().ui, b'differential.setdiffproperty', params)


def createdifferentialrevision(
    ctx,
    revid=None,
    parentrevphid=None,
    oldnode=None,
    olddiff=None,
    actions=None,
    comment=None,
):
    """create or update a Differential Revision

    If revid is None, create a new Differential Revision, otherwise update
    revid. If parentrevphid is not None, set it as a dependency.

    If oldnode is not None, check if the patch content (without commit message
    and metadata) has changed before creating another diff.

    If actions is not None, they will be appended to the transaction.
    """
    repo = ctx.repo()
    if oldnode:
        diffopts = mdiff.diffopts(git=True, context=32767)
        oldctx = repo.unfiltered()[oldnode]
        neednewdiff = getdiff(ctx, diffopts) != getdiff(oldctx, diffopts)
    else:
        neednewdiff = True

    transactions = []
    if neednewdiff:
        diff = creatediff(ctx)
        transactions.append({b'type': b'update', b'value': diff[b'phid']})
        if comment:
            transactions.append({b'type': b'comment', b'value': comment})
    else:
        # Even if we don't need to upload a new diff because the patch content
        # does not change. We might still need to update its metadata so
        # pushers could know the correct node metadata.
        assert olddiff
        diff = olddiff
    writediffproperties(ctx, diff)

    # Set the parent Revision every time, so commit re-ordering is picked-up
    if parentrevphid:
        transactions.append(
            {b'type': b'parents.set', b'value': [parentrevphid]}
        )

    if actions:
        transactions += actions

    # Parse commit message and update related fields.
    desc = ctx.description()
    info = callconduit(
        repo.ui, b'differential.parsecommitmessage', {b'corpus': desc}
    )
    for k, v in info[b'fields'].items():
        if k in [b'title', b'summary', b'testPlan']:
            transactions.append({b'type': k, b'value': v})

    params = {b'transactions': transactions}
    if revid is not None:
        # Update an existing Differential Revision
        params[b'objectIdentifier'] = revid

    revision = callconduit(repo.ui, b'differential.revision.edit', params)
    if not revision:
        raise error.Abort(_(b'cannot create revision for %s') % ctx)

    return revision, diff


def userphids(repo, names):
    """convert user names to PHIDs"""
    names = [name.lower() for name in names]
    query = {b'constraints': {b'usernames': names}}
    result = callconduit(repo.ui, b'user.search', query)
    # username not found is not an error of the API. So check if we have missed
    # some names here.
    data = result[b'data']
    resolved = set(entry[b'fields'][b'username'].lower() for entry in data)
    unresolved = set(names) - resolved
    if unresolved:
        raise error.Abort(
            _(b'unknown username: %s') % b' '.join(sorted(unresolved))
        )
    return [entry[b'phid'] for entry in data]


@vcrcommand(
    b'phabsend',
    [
        (b'r', b'rev', [], _(b'revisions to send'), _(b'REV')),
        (b'', b'amend', True, _(b'update commit messages')),
        (b'', b'reviewer', [], _(b'specify reviewers')),
        (b'', b'blocker', [], _(b'specify blocking reviewers')),
        (
            b'm',
            b'comment',
            b'',
            _(b'add a comment to Revisions with new/updated Diffs'),
        ),
        (b'', b'confirm', None, _(b'ask for confirmation before sending')),
    ],
    _(b'REV [OPTIONS]'),
    helpcategory=command.CATEGORY_IMPORT_EXPORT,
)
def phabsend(ui, repo, *revs, **opts):
    """upload changesets to Phabricator

    If there are multiple revisions specified, they will be send as a stack
    with a linear dependencies relationship using the order specified by the
    revset.

    For the first time uploading changesets, local tags will be created to
    maintain the association. After the first time, phabsend will check
    obsstore and tags information so it can figure out whether to update an
    existing Differential Revision, or create a new one.

    If --amend is set, update commit messages so they have the
    ``Differential Revision`` URL, remove related tags. This is similar to what
    arcanist will do, and is more desired in author-push workflows. Otherwise,
    use local tags to record the ``Differential Revision`` association.

    The --confirm option lets you confirm changesets before sending them. You
    can also add following to your configuration file to make it default
    behaviour::

        [phabsend]
        confirm = true

    phabsend will check obsstore and the above association to decide whether to
    update an existing Differential Revision, or create a new one.
    """
    opts = pycompat.byteskwargs(opts)
    revs = list(revs) + opts.get(b'rev', [])
    revs = scmutil.revrange(repo, revs)
    revs.sort()  # ascending order to preserve topological parent/child in phab

    if not revs:
        raise error.Abort(_(b'phabsend requires at least one changeset'))
    if opts.get(b'amend'):
        cmdutil.checkunfinished(repo)

    # {newnode: (oldnode, olddiff, olddrev}
    oldmap = getoldnodedrevmap(repo, [repo[r].node() for r in revs])

    confirm = ui.configbool(b'phabsend', b'confirm')
    confirm |= bool(opts.get(b'confirm'))
    if confirm:
        confirmed = _confirmbeforesend(repo, revs, oldmap)
        if not confirmed:
            raise error.Abort(_(b'phabsend cancelled'))

    actions = []
    reviewers = opts.get(b'reviewer', [])
    blockers = opts.get(b'blocker', [])
    phids = []
    if reviewers:
        phids.extend(userphids(repo, reviewers))
    if blockers:
        phids.extend(
            map(lambda phid: b'blocking(%s)' % phid, userphids(repo, blockers))
        )
    if phids:
        actions.append({b'type': b'reviewers.add', b'value': phids})

    drevids = []  # [int]
    diffmap = {}  # {newnode: diff}

    # Send patches one by one so we know their Differential Revision PHIDs and
    # can provide dependency relationship
    lastrevphid = None
    for rev in revs:
        ui.debug(b'sending rev %d\n' % rev)
        ctx = repo[rev]

        # Get Differential Revision ID
        oldnode, olddiff, revid = oldmap.get(ctx.node(), (None, None, None))
        if oldnode != ctx.node() or opts.get(b'amend'):
            # Create or update Differential Revision
            revision, diff = createdifferentialrevision(
                ctx,
                revid,
                lastrevphid,
                oldnode,
                olddiff,
                actions,
                opts.get(b'comment'),
            )
            diffmap[ctx.node()] = diff
            newrevid = int(revision[b'object'][b'id'])
            newrevphid = revision[b'object'][b'phid']
            if revid:
                action = b'updated'
            else:
                action = b'created'

            # Create a local tag to note the association, if commit message
            # does not have it already
            m = _differentialrevisiondescre.search(ctx.description())
            if not m or int(m.group('id')) != newrevid:
                tagname = b'D%d' % newrevid
                tags.tag(
                    repo,
                    tagname,
                    ctx.node(),
                    message=None,
                    user=None,
                    date=None,
                    local=True,
                )
        else:
            # Nothing changed. But still set "newrevphid" so the next revision
            # could depend on this one and "newrevid" for the summary line.
            newrevphid = querydrev(repo, b'%d' % revid)[0][b'phid']
            newrevid = revid
            action = b'skipped'

        actiondesc = ui.label(
            {
                b'created': _(b'created'),
                b'skipped': _(b'skipped'),
                b'updated': _(b'updated'),
            }[action],
            b'phabricator.action.%s' % action,
        )
        drevdesc = ui.label(b'D%d' % newrevid, b'phabricator.drev')
        nodedesc = ui.label(bytes(ctx), b'phabricator.node')
        desc = ui.label(ctx.description().split(b'\n')[0], b'phabricator.desc')
        ui.write(
            _(b'%s - %s - %s: %s\n') % (drevdesc, actiondesc, nodedesc, desc)
        )
        drevids.append(newrevid)
        lastrevphid = newrevphid

    # Update commit messages and remove tags
    if opts.get(b'amend'):
        unfi = repo.unfiltered()
        drevs = callconduit(ui, b'differential.query', {b'ids': drevids})
        with repo.wlock(), repo.lock(), repo.transaction(b'phabsend'):
            wnode = unfi[b'.'].node()
            mapping = {}  # {oldnode: [newnode]}
            for i, rev in enumerate(revs):
                old = unfi[rev]
                drevid = drevids[i]
                drev = [d for d in drevs if int(d[b'id']) == drevid][0]
                newdesc = getdescfromdrev(drev)
                # Make sure commit message contain "Differential Revision"
                if old.description() != newdesc:
                    if old.phase() == phases.public:
                        ui.warn(
                            _(b"warning: not updating public commit %s\n")
                            % scmutil.formatchangeid(old)
                        )
                        continue
                    parents = [
                        mapping.get(old.p1().node(), (old.p1(),))[0],
                        mapping.get(old.p2().node(), (old.p2(),))[0],
                    ]
                    new = context.metadataonlyctx(
                        repo,
                        old,
                        parents=parents,
                        text=newdesc,
                        user=old.user(),
                        date=old.date(),
                        extra=old.extra(),
                    )

                    newnode = new.commit()

                    mapping[old.node()] = [newnode]
                    # Update diff property
                    # If it fails just warn and keep going, otherwise the DREV
                    # associations will be lost
                    try:
                        writediffproperties(unfi[newnode], diffmap[old.node()])
                    except util.urlerr.urlerror:
                        ui.warnnoi18n(
                            b'Failed to update metadata for D%d\n' % drevid
                        )
                # Remove local tags since it's no longer necessary
                tagname = b'D%d' % drevid
                if tagname in repo.tags():
                    tags.tag(
                        repo,
                        tagname,
                        nullid,
                        message=None,
                        user=None,
                        date=None,
                        local=True,
                    )
            scmutil.cleanupnodes(repo, mapping, b'phabsend', fixphase=True)
            if wnode in mapping:
                unfi.setparents(mapping[wnode][0])


# Map from "hg:meta" keys to header understood by "hg import". The order is
# consistent with "hg export" output.
_metanamemap = util.sortdict(
    [
        (b'user', b'User'),
        (b'date', b'Date'),
        (b'branch', b'Branch'),
        (b'node', b'Node ID'),
        (b'parent', b'Parent '),
    ]
)


def _confirmbeforesend(repo, revs, oldmap):
    url, token = readurltoken(repo.ui)
    ui = repo.ui
    for rev in revs:
        ctx = repo[rev]
        desc = ctx.description().splitlines()[0]
        oldnode, olddiff, drevid = oldmap.get(ctx.node(), (None, None, None))
        if drevid:
            drevdesc = ui.label(b'D%d' % drevid, b'phabricator.drev')
        else:
            drevdesc = ui.label(_(b'NEW'), b'phabricator.drev')

        ui.write(
            _(b'%s - %s: %s\n')
            % (
                drevdesc,
                ui.label(bytes(ctx), b'phabricator.node'),
                ui.label(desc, b'phabricator.desc'),
            )
        )

    if ui.promptchoice(
        _(b'Send the above changes to %s (yn)?$$ &Yes $$ &No') % url
    ):
        return False

    return True


_knownstatusnames = {
    b'accepted',
    b'needsreview',
    b'needsrevision',
    b'closed',
    b'abandoned',
    b'changesplanned',
}


def _getstatusname(drev):
    """get normalized status name from a Differential Revision"""
    return drev[b'statusName'].replace(b' ', b'').lower()


# Small language to specify differential revisions. Support symbols: (), :X,
# +, and -.

_elements = {
    # token-type: binding-strength, primary, prefix, infix, suffix
    b'(': (12, None, (b'group', 1, b')'), None, None),
    b':': (8, None, (b'ancestors', 8), None, None),
    b'&': (5, None, None, (b'and_', 5), None),
    b'+': (4, None, None, (b'add', 4), None),
    b'-': (4, None, None, (b'sub', 4), None),
    b')': (0, None, None, None, None),
    b'symbol': (0, b'symbol', None, None, None),
    b'end': (0, None, None, None, None),
}


def _tokenize(text):
    view = memoryview(text)  # zero-copy slice
    special = b'():+-& '
    pos = 0
    length = len(text)
    while pos < length:
        symbol = b''.join(
            itertools.takewhile(
                lambda ch: ch not in special, pycompat.iterbytestr(view[pos:])
            )
        )
        if symbol:
            yield (b'symbol', symbol, pos)
            pos += len(symbol)
        else:  # special char, ignore space
            if text[pos : pos + 1] != b' ':
                yield (text[pos : pos + 1], None, pos)
            pos += 1
    yield (b'end', None, pos)


def _parse(text):
    tree, pos = parser.parser(_elements).parse(_tokenize(text))
    if pos != len(text):
        raise error.ParseError(b'invalid token', pos)
    return tree


def _parsedrev(symbol):
    """str -> int or None, ex. 'D45' -> 45; '12' -> 12; 'x' -> None"""
    if symbol.startswith(b'D') and symbol[1:].isdigit():
        return int(symbol[1:])
    if symbol.isdigit():
        return int(symbol)


def _prefetchdrevs(tree):
    """return ({single-drev-id}, {ancestor-drev-id}) to prefetch"""
    drevs = set()
    ancestordrevs = set()
    op = tree[0]
    if op == b'symbol':
        r = _parsedrev(tree[1])
        if r:
            drevs.add(r)
    elif op == b'ancestors':
        r, a = _prefetchdrevs(tree[1])
        drevs.update(r)
        ancestordrevs.update(r)
        ancestordrevs.update(a)
    else:
        for t in tree[1:]:
            r, a = _prefetchdrevs(t)
            drevs.update(r)
            ancestordrevs.update(a)
    return drevs, ancestordrevs


def querydrev(repo, spec):
    """return a list of "Differential Revision" dicts

    spec is a string using a simple query language, see docstring in phabread
    for details.

    A "Differential Revision dict" looks like:

        {
            "id": "2",
            "phid": "PHID-DREV-672qvysjcczopag46qty",
            "title": "example",
            "uri": "https://phab.example.com/D2",
            "dateCreated": "1499181406",
            "dateModified": "1499182103",
            "authorPHID": "PHID-USER-tv3ohwc4v4jeu34otlye",
            "status": "0",
            "statusName": "Needs Review",
            "properties": [],
            "branch": null,
            "summary": "",
            "testPlan": "",
            "lineCount": "2",
            "activeDiffPHID": "PHID-DIFF-xoqnjkobbm6k4dk6hi72",
            "diffs": [
              "3",
              "4",
            ],
            "commits": [],
            "reviewers": [],
            "ccs": [],
            "hashes": [],
            "auxiliary": {
              "phabricator:projects": [],
              "phabricator:depends-on": [
                "PHID-DREV-gbapp366kutjebt7agcd"
              ]
            },
            "repositoryPHID": "PHID-REPO-hub2hx62ieuqeheznasv",
            "sourcePath": null
        }
    """

    def fetch(params):
        """params -> single drev or None"""
        key = (params.get(b'ids') or params.get(b'phids') or [None])[0]
        if key in prefetched:
            return prefetched[key]
        drevs = callconduit(repo.ui, b'differential.query', params)
        # Fill prefetched with the result
        for drev in drevs:
            prefetched[drev[b'phid']] = drev
            prefetched[int(drev[b'id'])] = drev
        if key not in prefetched:
            raise error.Abort(
                _(b'cannot get Differential Revision %r') % params
            )
        return prefetched[key]

    def getstack(topdrevids):
        """given a top, get a stack from the bottom, [id] -> [id]"""
        visited = set()
        result = []
        queue = [{b'ids': [i]} for i in topdrevids]
        while queue:
            params = queue.pop()
            drev = fetch(params)
            if drev[b'id'] in visited:
                continue
            visited.add(drev[b'id'])
            result.append(int(drev[b'id']))
            auxiliary = drev.get(b'auxiliary', {})
            depends = auxiliary.get(b'phabricator:depends-on', [])
            for phid in depends:
                queue.append({b'phids': [phid]})
        result.reverse()
        return smartset.baseset(result)

    # Initialize prefetch cache
    prefetched = {}  # {id or phid: drev}

    tree = _parse(spec)
    drevs, ancestordrevs = _prefetchdrevs(tree)

    # developer config: phabricator.batchsize
    batchsize = repo.ui.configint(b'phabricator', b'batchsize')

    # Prefetch Differential Revisions in batch
    tofetch = set(drevs)
    for r in ancestordrevs:
        tofetch.update(range(max(1, r - batchsize), r + 1))
    if drevs:
        fetch({b'ids': list(tofetch)})
    validids = sorted(set(getstack(list(ancestordrevs))) | set(drevs))

    # Walk through the tree, return smartsets
    def walk(tree):
        op = tree[0]
        if op == b'symbol':
            drev = _parsedrev(tree[1])
            if drev:
                return smartset.baseset([drev])
            elif tree[1] in _knownstatusnames:
                drevs = [
                    r
                    for r in validids
                    if _getstatusname(prefetched[r]) == tree[1]
                ]
                return smartset.baseset(drevs)
            else:
                raise error.Abort(_(b'unknown symbol: %s') % tree[1])
        elif op in {b'and_', b'add', b'sub'}:
            assert len(tree) == 3
            return getattr(operator, op)(walk(tree[1]), walk(tree[2]))
        elif op == b'group':
            return walk(tree[1])
        elif op == b'ancestors':
            return getstack(walk(tree[1]))
        else:
            raise error.ProgrammingError(b'illegal tree: %r' % tree)

    return [prefetched[r] for r in walk(tree)]


def getdescfromdrev(drev):
    """get description (commit message) from "Differential Revision"

    This is similar to differential.getcommitmessage API. But we only care
    about limited fields: title, summary, test plan, and URL.
    """
    title = drev[b'title']
    summary = drev[b'summary'].rstrip()
    testplan = drev[b'testPlan'].rstrip()
    if testplan:
        testplan = b'Test Plan:\n%s' % testplan
    uri = b'Differential Revision: %s' % drev[b'uri']
    return b'\n\n'.join(filter(None, [title, summary, testplan, uri]))


def getdiffmeta(diff):
    """get commit metadata (date, node, user, p1) from a diff object

    The metadata could be "hg:meta", sent by phabsend, like:

        "properties": {
          "hg:meta": {
            "date": "1499571514 25200",
            "node": "98c08acae292b2faf60a279b4189beb6cff1414d",
            "user": "Foo Bar <foo@example.com>",
            "parent": "6d0abad76b30e4724a37ab8721d630394070fe16"
          }
        }

    Or converted from "local:commits", sent by "arc", like:

        "properties": {
          "local:commits": {
            "98c08acae292b2faf60a279b4189beb6cff1414d": {
              "author": "Foo Bar",
              "time": 1499546314,
              "branch": "default",
              "tag": "",
              "commit": "98c08acae292b2faf60a279b4189beb6cff1414d",
              "rev": "98c08acae292b2faf60a279b4189beb6cff1414d",
              "local": "1000",
              "parents": ["6d0abad76b30e4724a37ab8721d630394070fe16"],
              "summary": "...",
              "message": "...",
              "authorEmail": "foo@example.com"
            }
          }
        }

    Note: metadata extracted from "local:commits" will lose time zone
    information.
    """
    props = diff.get(b'properties') or {}
    meta = props.get(b'hg:meta')
    if not meta:
        if props.get(b'local:commits'):
            commit = sorted(props[b'local:commits'].values())[0]
            meta = {}
            if b'author' in commit and b'authorEmail' in commit:
                meta[b'user'] = b'%s <%s>' % (
                    commit[b'author'],
                    commit[b'authorEmail'],
                )
            if b'time' in commit:
                meta[b'date'] = b'%d 0' % int(commit[b'time'])
            if b'branch' in commit:
                meta[b'branch'] = commit[b'branch']
            node = commit.get(b'commit', commit.get(b'rev'))
            if node:
                meta[b'node'] = node
            if len(commit.get(b'parents', ())) >= 1:
                meta[b'parent'] = commit[b'parents'][0]
        else:
            meta = {}
    if b'date' not in meta and b'dateCreated' in diff:
        meta[b'date'] = b'%s 0' % diff[b'dateCreated']
    if b'branch' not in meta and diff.get(b'branch'):
        meta[b'branch'] = diff[b'branch']
    if b'parent' not in meta and diff.get(b'sourceControlBaseRevision'):
        meta[b'parent'] = diff[b'sourceControlBaseRevision']
    return meta


def readpatch(repo, drevs, write):
    """generate plain-text patch readable by 'hg import'

    write is usually ui.write. drevs is what "querydrev" returns, results of
    "differential.query".
    """
    # Prefetch hg:meta property for all diffs
    diffids = sorted(set(max(int(v) for v in drev[b'diffs']) for drev in drevs))
    diffs = callconduit(repo.ui, b'differential.querydiffs', {b'ids': diffids})

    # Generate patch for each drev
    for drev in drevs:
        repo.ui.note(_(b'reading D%s\n') % drev[b'id'])

        diffid = max(int(v) for v in drev[b'diffs'])
        body = callconduit(
            repo.ui, b'differential.getrawdiff', {b'diffID': diffid}
        )
        desc = getdescfromdrev(drev)
        header = b'# HG changeset patch\n'

        # Try to preserve metadata from hg:meta property. Write hg patch
        # headers that can be read by the "import" command. See patchheadermap
        # and extract in mercurial/patch.py for supported headers.
        meta = getdiffmeta(diffs[b'%d' % diffid])
        for k in _metanamemap.keys():
            if k in meta:
                header += b'# %s %s\n' % (_metanamemap[k], meta[k])

        content = b'%s%s\n%s' % (header, desc, body)
        write(content)


@vcrcommand(
    b'phabread',
    [(b'', b'stack', False, _(b'read dependencies'))],
    _(b'DREVSPEC [OPTIONS]'),
    helpcategory=command.CATEGORY_IMPORT_EXPORT,
)
def phabread(ui, repo, spec, **opts):
    """print patches from Phabricator suitable for importing

    DREVSPEC could be a Differential Revision identity, like ``D123``, or just
    the number ``123``. It could also have common operators like ``+``, ``-``,
    ``&``, ``(``, ``)`` for complex queries. Prefix ``:`` could be used to
    select a stack.

    ``abandoned``, ``accepted``, ``closed``, ``needsreview``, ``needsrevision``
    could be used to filter patches by status. For performance reason, they
    only represent a subset of non-status selections and cannot be used alone.

    For example, ``:D6+8-(2+D4)`` selects a stack up to D6, plus D8 and exclude
    D2 and D4. ``:D9 & needsreview`` selects "Needs Review" revisions in a
    stack up to D9.

    If --stack is given, follow dependencies information and read all patches.
    It is equivalent to the ``:`` operator.
    """
    opts = pycompat.byteskwargs(opts)
    if opts.get(b'stack'):
        spec = b':(%s)' % spec
    drevs = querydrev(repo, spec)
    readpatch(repo, drevs, ui.write)


@vcrcommand(
    b'phabupdate',
    [
        (b'', b'accept', False, _(b'accept revisions')),
        (b'', b'reject', False, _(b'reject revisions')),
        (b'', b'abandon', False, _(b'abandon revisions')),
        (b'', b'reclaim', False, _(b'reclaim revisions')),
        (b'm', b'comment', b'', _(b'comment on the last revision')),
    ],
    _(b'DREVSPEC [OPTIONS]'),
    helpcategory=command.CATEGORY_IMPORT_EXPORT,
)
def phabupdate(ui, repo, spec, **opts):
    """update Differential Revision in batch

    DREVSPEC selects revisions. See :hg:`help phabread` for its usage.
    """
    opts = pycompat.byteskwargs(opts)
    flags = [n for n in b'accept reject abandon reclaim'.split() if opts.get(n)]
    if len(flags) > 1:
        raise error.Abort(_(b'%s cannot be used together') % b', '.join(flags))

    actions = []
    for f in flags:
        actions.append({b'type': f, b'value': True})

    drevs = querydrev(repo, spec)
    for i, drev in enumerate(drevs):
        if i + 1 == len(drevs) and opts.get(b'comment'):
            actions.append({b'type': b'comment', b'value': opts[b'comment']})
        if actions:
            params = {
                b'objectIdentifier': drev[b'phid'],
                b'transactions': actions,
            }
            callconduit(ui, b'differential.revision.edit', params)


@eh.templatekeyword(b'phabreview', requires={b'ctx'})
def template_review(context, mapping):
    """:phabreview: Object describing the review for this changeset.
    Has attributes `url` and `id`.
    """
    ctx = context.resource(mapping, b'ctx')
    m = _differentialrevisiondescre.search(ctx.description())
    if m:
        return templateutil.hybriddict(
            {b'url': m.group('url'), b'id': b"D%s" % m.group('id'),}
        )
    else:
        tags = ctx.repo().nodetags(ctx.node())
        for t in tags:
            if _differentialrevisiontagre.match(t):
                url = ctx.repo().ui.config(b'phabricator', b'url')
                if not url.endswith(b'/'):
                    url += b'/'
                url += t

                return templateutil.hybriddict({b'url': url, b'id': t,})
    return None


@eh.templatekeyword(b'phabstatus', requires={b'ctx', b'repo', b'ui'})
def template_status(context, mapping):
    """:phabstatus: String. Status of Phabricator differential.
    """
    ctx = context.resource(mapping, b'ctx')
    repo = context.resource(mapping, b'repo')
    ui = context.resource(mapping, b'ui')

    rev = ctx.rev()
    try:
        drevid = getdrevmap(repo, [rev])[rev]
    except KeyError:
        return None
    drevs = callconduit(ui, b'differential.query', {b'ids': [drevid]})
    for drev in drevs:
        if int(drev[b'id']) == drevid:
            return templateutil.hybriddict(
                {b'url': drev[b'uri'], b'status': drev[b'statusName'],}
            )
    return None


@show.showview(b'phabstatus', csettopic=b'work')
def phabstatusshowview(ui, repo, displayer):
    """Phabricator differiential status"""
    revs = repo.revs('sort(_underway(), topo)')
    drevmap = getdrevmap(repo, revs)
    unknownrevs, drevids, revsbydrevid = [], set([]), {}
    for rev, drevid in pycompat.iteritems(drevmap):
        if drevid is not None:
            drevids.add(drevid)
            revsbydrevid.setdefault(drevid, set([])).add(rev)
        else:
            unknownrevs.append(rev)

    drevs = callconduit(ui, b'differential.query', {b'ids': list(drevids)})
    drevsbyrev = {}
    for drev in drevs:
        for rev in revsbydrevid[int(drev[b'id'])]:
            drevsbyrev[rev] = drev

    def phabstatus(ctx):
        drev = drevsbyrev[ctx.rev()]
        status = ui.label(
            b'%(statusName)s' % drev,
            b'phabricator.status.%s' % _getstatusname(drev),
        )
        ui.write(b"\n%s %s\n" % (drev[b'uri'], status))

    revs -= smartset.baseset(unknownrevs)
    revdag = graphmod.dagwalker(repo, revs)

    ui.setconfig(b'experimental', b'graphshorten', True)
    displayer._exthook = phabstatus
    nodelen = show.longestshortest(repo, revs)
    logcmdutil.displaygraph(
        ui,
        repo,
        revdag,
        displayer,
        graphmod.asciiedges,
        props={b'nodelen': nodelen},
    )
