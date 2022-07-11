from __future__ import absolute_import

import os

from . import (
    encoding,
    pycompat,
    util,
    win32,
)

try:
    import _winreg as winreg  # pytype: disable=import-error

    winreg.CloseKey
except ImportError:
    # py2 only
    import winreg  # pytype: disable=import-error

# MS-DOS 'more' is the only pager available by default on Windows.
fallbackpager = b'more'


def systemrcpath():
    '''return default os-specific hgrc search path'''
    rcpath = []
    filename = win32.executablepath()
    # Use mercurial.ini found in directory with hg.exe
    progrc = os.path.join(os.path.dirname(filename), b'mercurial.ini')
    rcpath.append(progrc)

    def _processdir(progrcd):
        if os.path.isdir(progrcd):
            for f, kind in util.listdir(progrcd):
                if f.endswith(b'.rc'):
                    rcpath.append(os.path.join(progrcd, f))

    # Use hgrc.d found in directory with hg.exe
    _processdir(os.path.join(os.path.dirname(filename), b'hgrc.d'))

    # treat a PROGRAMDATA directory as equivalent to /etc/mercurial
    programdata = encoding.environ.get(b'PROGRAMDATA')
    if programdata:
        programdata = os.path.join(programdata, b'Mercurial')
        _processdir(os.path.join(programdata, b'hgrc.d'))

        ini = os.path.join(programdata, b'mercurial.ini')
        if os.path.isfile(ini):
            rcpath.append(ini)

        ini = os.path.join(programdata, b'hgrc')
        if os.path.isfile(ini):
            rcpath.append(ini)

    # next look for a system rcpath in the registry
    value = util.lookupreg(
        b'SOFTWARE\\Mercurial', None, winreg.HKEY_LOCAL_MACHINE
    )
    if value and isinstance(value, bytes):
        value = util.localpath(value)
        for p in value.split(pycompat.ospathsep):
            if p.lower().endswith(b'mercurial.ini'):
                rcpath.append(p)
            else:
                _processdir(p)
    return rcpath


def userrcpath():
    '''return os-specific hgrc search path to the user dir'''
    home = os.path.expanduser(b'~')
    path = [os.path.join(home, b'mercurial.ini'), os.path.join(home, b'.hgrc')]
    userprofile = encoding.environ.get(b'USERPROFILE')
    if userprofile and userprofile != home:
        path.append(os.path.join(userprofile, b'mercurial.ini'))
        path.append(os.path.join(userprofile, b'.hgrc'))
    return path


def termsize(ui):
    return win32.termsize()
