# Copyright (C) 2006 - Marco Barisione <marco@barisione.org>
#
# This is a small extension for Mercurial (https://mercurial-scm.org/)
# that removes files not known to mercurial
#
# This program was inspired by the "cvspurge" script contained in CVS
# utilities (http://www.red-bean.com/cvsutils/).
#
# For help on the usage of "hg purge" use:
#  hg help purge
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

'''command to delete untracked files from the working directory'''
from __future__ import absolute_import

from mercurial.i18n import _
from mercurial import (
    cmdutil,
    merge as mergemod,
    pycompat,
    registrar,
    scmutil,
)

cmdtable = {}
command = registrar.command(cmdtable)
# Note for extension authors: ONLY specify testedwith = 'ships-with-hg-core' for
# extensions which SHIP WITH MERCURIAL. Non-mainline extensions should
# be specifying the version(s) of Mercurial they are tested with, or
# leave the attribute unspecified.
testedwith = b'ships-with-hg-core'


@command(
    b'purge|clean',
    [
        (b'a', b'abort-on-err', None, _(b'abort if an error occurs')),
        (b'', b'all', None, _(b'purge ignored files too')),
        (b'', b'dirs', None, _(b'purge empty directories')),
        (b'', b'files', None, _(b'purge files')),
        (b'p', b'print', None, _(b'print filenames instead of deleting them')),
        (
            b'0',
            b'print0',
            None,
            _(
                b'end filenames with NUL, for use with xargs'
                b' (implies -p/--print)'
            ),
        ),
    ]
    + cmdutil.walkopts,
    _(b'hg purge [OPTION]... [DIR]...'),
    helpcategory=command.CATEGORY_MAINTENANCE,
)
def purge(ui, repo, *dirs, **opts):
    '''removes files not tracked by Mercurial

    Delete files not known to Mercurial. This is useful to test local
    and uncommitted changes in an otherwise-clean source tree.

    This means that purge will delete the following by default:

    - Unknown files: files marked with "?" by :hg:`status`
    - Empty directories: in fact Mercurial ignores directories unless
      they contain files under source control management

    But it will leave untouched:

    - Modified and unmodified tracked files
    - Ignored files (unless --all is specified)
    - New files added to the repository (with :hg:`add`)

    The --files and --dirs options can be used to direct purge to delete
    only files, only directories, or both. If neither option is given,
    both will be deleted.

    If directories are given on the command line, only files in these
    directories are considered.

    Be careful with purge, as you could irreversibly delete some files
    you forgot to add to the repository. If you only want to print the
    list of files that this program would delete, use the --print
    option.
    '''
    opts = pycompat.byteskwargs(opts)

    act = not opts.get(b'print')
    eol = b'\n'
    if opts.get(b'print0'):
        eol = b'\0'
        act = False  # --print0 implies --print

    removefiles = opts.get(b'files')
    removedirs = opts.get(b'dirs')

    if not removefiles and not removedirs:
        removefiles = True
        removedirs = True

    match = scmutil.match(repo[None], dirs, opts)

    paths = mergemod.purge(
        repo,
        match,
        ignored=opts.get(b'all', False),
        removeemptydirs=removedirs,
        removefiles=removefiles,
        abortonerror=opts.get(b'abort_on_err'),
        noop=not act,
    )

    for path in paths:
        if not act:
            ui.write(b'%s%s' % (path, eol))
