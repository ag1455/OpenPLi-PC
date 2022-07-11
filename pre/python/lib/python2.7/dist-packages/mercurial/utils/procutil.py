# procutil.py - utility for managing processes and executable environment
#
#  Copyright 2005 K. Thananchayan <thananck@yahoo.com>
#  Copyright 2005-2007 Matt Mackall <mpm@selenic.com>
#  Copyright 2006 Vadim Gelfer <vadim.gelfer@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

import contextlib
import errno
import io
import os
import signal
import subprocess
import sys
import time

from ..i18n import _
from ..pycompat import (
    getattr,
    open,
)

from .. import (
    encoding,
    error,
    policy,
    pycompat,
)

# Import like this to keep import-checker happy
from ..utils import resourceutil

osutil = policy.importmod('osutil')

stderr = pycompat.stderr
stdin = pycompat.stdin
stdout = pycompat.stdout


def isatty(fp):
    try:
        return fp.isatty()
    except AttributeError:
        return False


# glibc determines buffering on first write to stdout - if we replace a TTY
# destined stdout with a pipe destined stdout (e.g. pager), we want line
# buffering (or unbuffered, on Windows)
if isatty(stdout):
    if pycompat.iswindows:
        # Windows doesn't support line buffering
        stdout = os.fdopen(stdout.fileno(), 'wb', 0)
    elif not pycompat.ispy3:
        # on Python 3, stdout (sys.stdout.buffer) is already line buffered and
        # buffering=1 is not handled in binary mode
        stdout = os.fdopen(stdout.fileno(), 'wb', 1)

if pycompat.iswindows:
    from .. import windows as platform

    stdout = platform.winstdout(stdout)
else:
    from .. import posix as platform

findexe = platform.findexe
_gethgcmd = platform.gethgcmd
getuser = platform.getuser
getpid = os.getpid
hidewindow = platform.hidewindow
quotecommand = platform.quotecommand
readpipe = platform.readpipe
setbinary = platform.setbinary
setsignalhandler = platform.setsignalhandler
shellquote = platform.shellquote
shellsplit = platform.shellsplit
spawndetached = platform.spawndetached
sshargs = platform.sshargs
testpid = platform.testpid

try:
    setprocname = osutil.setprocname
except AttributeError:
    pass
try:
    unblocksignal = osutil.unblocksignal
except AttributeError:
    pass

closefds = pycompat.isposix


def explainexit(code):
    """return a message describing a subprocess status
    (codes from kill are negative - not os.system/wait encoding)"""
    if code >= 0:
        return _(b"exited with status %d") % code
    return _(b"killed by signal %d") % -code


class _pfile(object):
    """File-like wrapper for a stream opened by subprocess.Popen()"""

    def __init__(self, proc, fp):
        self._proc = proc
        self._fp = fp

    def close(self):
        # unlike os.popen(), this returns an integer in subprocess coding
        self._fp.close()
        return self._proc.wait()

    def __iter__(self):
        return iter(self._fp)

    def __getattr__(self, attr):
        return getattr(self._fp, attr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()


def popen(cmd, mode=b'rb', bufsize=-1):
    if mode == b'rb':
        return _popenreader(cmd, bufsize)
    elif mode == b'wb':
        return _popenwriter(cmd, bufsize)
    raise error.ProgrammingError(b'unsupported mode: %r' % mode)


def _popenreader(cmd, bufsize):
    p = subprocess.Popen(
        tonativestr(quotecommand(cmd)),
        shell=True,
        bufsize=bufsize,
        close_fds=closefds,
        stdout=subprocess.PIPE,
    )
    return _pfile(p, p.stdout)


def _popenwriter(cmd, bufsize):
    p = subprocess.Popen(
        tonativestr(quotecommand(cmd)),
        shell=True,
        bufsize=bufsize,
        close_fds=closefds,
        stdin=subprocess.PIPE,
    )
    return _pfile(p, p.stdin)


def popen2(cmd, env=None):
    # Setting bufsize to -1 lets the system decide the buffer size.
    # The default for bufsize is 0, meaning unbuffered. This leads to
    # poor performance on Mac OS X: http://bugs.python.org/issue4194
    p = subprocess.Popen(
        tonativestr(cmd),
        shell=True,
        bufsize=-1,
        close_fds=closefds,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env=tonativeenv(env),
    )
    return p.stdin, p.stdout


def popen3(cmd, env=None):
    stdin, stdout, stderr, p = popen4(cmd, env)
    return stdin, stdout, stderr


def popen4(cmd, env=None, bufsize=-1):
    p = subprocess.Popen(
        tonativestr(cmd),
        shell=True,
        bufsize=bufsize,
        close_fds=closefds,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=tonativeenv(env),
    )
    return p.stdin, p.stdout, p.stderr, p


def pipefilter(s, cmd):
    '''filter string S through command CMD, returning its output'''
    p = subprocess.Popen(
        tonativestr(cmd),
        shell=True,
        close_fds=closefds,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    pout, perr = p.communicate(s)
    return pout


def tempfilter(s, cmd):
    '''filter string S through a pair of temporary files with CMD.
    CMD is used as a template to create the real command to be run,
    with the strings INFILE and OUTFILE replaced by the real names of
    the temporary files generated.'''
    inname, outname = None, None
    try:
        infd, inname = pycompat.mkstemp(prefix=b'hg-filter-in-')
        fp = os.fdopen(infd, 'wb')
        fp.write(s)
        fp.close()
        outfd, outname = pycompat.mkstemp(prefix=b'hg-filter-out-')
        os.close(outfd)
        cmd = cmd.replace(b'INFILE', inname)
        cmd = cmd.replace(b'OUTFILE', outname)
        code = system(cmd)
        if pycompat.sysplatform == b'OpenVMS' and code & 1:
            code = 0
        if code:
            raise error.Abort(
                _(b"command '%s' failed: %s") % (cmd, explainexit(code))
            )
        with open(outname, b'rb') as fp:
            return fp.read()
    finally:
        try:
            if inname:
                os.unlink(inname)
        except OSError:
            pass
        try:
            if outname:
                os.unlink(outname)
        except OSError:
            pass


_filtertable = {
    b'tempfile:': tempfilter,
    b'pipe:': pipefilter,
}


def filter(s, cmd):
    """filter a string through a command that transforms its input to its
    output"""
    for name, fn in pycompat.iteritems(_filtertable):
        if cmd.startswith(name):
            return fn(s, cmd[len(name) :].lstrip())
    return pipefilter(s, cmd)


_hgexecutable = None


def hgexecutable():
    """return location of the 'hg' executable.

    Defaults to $HG or 'hg' in the search path.
    """
    if _hgexecutable is None:
        hg = encoding.environ.get(b'HG')
        mainmod = sys.modules['__main__']
        if hg:
            _sethgexecutable(hg)
        elif resourceutil.mainfrozen():
            if getattr(sys, 'frozen', None) == 'macosx_app':
                # Env variable set by py2app
                _sethgexecutable(encoding.environ[b'EXECUTABLEPATH'])
            else:
                _sethgexecutable(pycompat.sysexecutable)
        elif (
            not pycompat.iswindows
            and os.path.basename(getattr(mainmod, '__file__', '')) == 'hg'
        ):
            _sethgexecutable(pycompat.fsencode(mainmod.__file__))
        else:
            _sethgexecutable(
                findexe(b'hg') or os.path.basename(pycompat.sysargv[0])
            )
    return _hgexecutable


def _sethgexecutable(path):
    """set location of the 'hg' executable"""
    global _hgexecutable
    _hgexecutable = path


def _testfileno(f, stdf):
    fileno = getattr(f, 'fileno', None)
    try:
        return fileno and fileno() == stdf.fileno()
    except io.UnsupportedOperation:
        return False  # fileno() raised UnsupportedOperation


def isstdin(f):
    return _testfileno(f, sys.__stdin__)


def isstdout(f):
    return _testfileno(f, sys.__stdout__)


def protectstdio(uin, uout):
    """Duplicate streams and redirect original if (uin, uout) are stdio

    If uin is stdin, it's redirected to /dev/null. If uout is stdout, it's
    redirected to stderr so the output is still readable.

    Returns (fin, fout) which point to the original (uin, uout) fds, but
    may be copy of (uin, uout). The returned streams can be considered
    "owned" in that print(), exec(), etc. never reach to them.
    """
    uout.flush()
    fin, fout = uin, uout
    if _testfileno(uin, stdin):
        newfd = os.dup(uin.fileno())
        nullfd = os.open(os.devnull, os.O_RDONLY)
        os.dup2(nullfd, uin.fileno())
        os.close(nullfd)
        fin = os.fdopen(newfd, 'rb')
    if _testfileno(uout, stdout):
        newfd = os.dup(uout.fileno())
        os.dup2(stderr.fileno(), uout.fileno())
        fout = os.fdopen(newfd, 'wb')
    return fin, fout


def restorestdio(uin, uout, fin, fout):
    """Restore (uin, uout) streams from possibly duplicated (fin, fout)"""
    uout.flush()
    for f, uif in [(fin, uin), (fout, uout)]:
        if f is not uif:
            os.dup2(f.fileno(), uif.fileno())
            f.close()


def shellenviron(environ=None):
    """return environ with optional override, useful for shelling out"""

    def py2shell(val):
        """convert python object into string that is useful to shell"""
        if val is None or val is False:
            return b'0'
        if val is True:
            return b'1'
        return pycompat.bytestr(val)

    env = dict(encoding.environ)
    if environ:
        env.update((k, py2shell(v)) for k, v in pycompat.iteritems(environ))
    env[b'HG'] = hgexecutable()
    return env


if pycompat.iswindows:

    def shelltonative(cmd, env):
        return platform.shelltocmdexe(  # pytype: disable=module-attr
            cmd, shellenviron(env)
        )

    tonativestr = encoding.strfromlocal
else:

    def shelltonative(cmd, env):
        return cmd

    tonativestr = pycompat.identity


def tonativeenv(env):
    '''convert the environment from bytes to strings suitable for Popen(), etc.
    '''
    return pycompat.rapply(tonativestr, env)


def system(cmd, environ=None, cwd=None, out=None):
    '''enhanced shell command execution.
    run with environment maybe modified, maybe in different dir.

    if out is specified, it is assumed to be a file-like object that has a
    write() method. stdout and stderr will be redirected to out.'''
    try:
        stdout.flush()
    except Exception:
        pass
    cmd = quotecommand(cmd)
    env = shellenviron(environ)
    if out is None or isstdout(out):
        rc = subprocess.call(
            tonativestr(cmd),
            shell=True,
            close_fds=closefds,
            env=tonativeenv(env),
            cwd=pycompat.rapply(tonativestr, cwd),
        )
    else:
        proc = subprocess.Popen(
            tonativestr(cmd),
            shell=True,
            close_fds=closefds,
            env=tonativeenv(env),
            cwd=pycompat.rapply(tonativestr, cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for line in iter(proc.stdout.readline, b''):
            out.write(line)
        proc.wait()
        rc = proc.returncode
    if pycompat.sysplatform == b'OpenVMS' and rc & 1:
        rc = 0
    return rc


_is_gui = None


def _gui():
    '''Are we running in a GUI?'''
    if pycompat.isdarwin:
        if b'SSH_CONNECTION' in encoding.environ:
            # handle SSH access to a box where the user is logged in
            return False
        elif getattr(osutil, 'isgui', None):
            # check if a CoreGraphics session is available
            return osutil.isgui()
        else:
            # pure build; use a safe default
            return True
    else:
        return pycompat.iswindows or encoding.environ.get(b"DISPLAY")


def gui():
    global _is_gui
    if _is_gui is None:
        _is_gui = _gui()
    return _is_gui


def hgcmd():
    """Return the command used to execute current hg

    This is different from hgexecutable() because on Windows we want
    to avoid things opening new shell windows like batch files, so we
    get either the python call or current executable.
    """
    if resourceutil.mainfrozen():
        if getattr(sys, 'frozen', None) == 'macosx_app':
            # Env variable set by py2app
            return [encoding.environ[b'EXECUTABLEPATH']]
        else:
            return [pycompat.sysexecutable]
    return _gethgcmd()


def rundetached(args, condfn):
    """Execute the argument list in a detached process.

    condfn is a callable which is called repeatedly and should return
    True once the child process is known to have started successfully.
    At this point, the child process PID is returned. If the child
    process fails to start or finishes before condfn() evaluates to
    True, return -1.
    """
    # Windows case is easier because the child process is either
    # successfully starting and validating the condition or exiting
    # on failure. We just poll on its PID. On Unix, if the child
    # process fails to start, it will be left in a zombie state until
    # the parent wait on it, which we cannot do since we expect a long
    # running process on success. Instead we listen for SIGCHLD telling
    # us our child process terminated.
    terminated = set()

    def handler(signum, frame):
        terminated.add(os.wait())

    prevhandler = None
    SIGCHLD = getattr(signal, 'SIGCHLD', None)
    if SIGCHLD is not None:
        prevhandler = signal.signal(SIGCHLD, handler)
    try:
        pid = spawndetached(args)
        while not condfn():
            if (pid in terminated or not testpid(pid)) and not condfn():
                return -1
            time.sleep(0.1)
        return pid
    finally:
        if prevhandler is not None:
            signal.signal(signal.SIGCHLD, prevhandler)


@contextlib.contextmanager
def uninterruptible(warn):
    """Inhibit SIGINT handling on a region of code.

    Note that if this is called in a non-main thread, it turns into a no-op.

    Args:
      warn: A callable which takes no arguments, and returns True if the
            previous signal handling should be restored.
    """

    oldsiginthandler = [signal.getsignal(signal.SIGINT)]
    shouldbail = []

    def disabledsiginthandler(*args):
        if warn():
            signal.signal(signal.SIGINT, oldsiginthandler[0])
            del oldsiginthandler[0]
        shouldbail.append(True)

    try:
        try:
            signal.signal(signal.SIGINT, disabledsiginthandler)
        except ValueError:
            # wrong thread, oh well, we tried
            del oldsiginthandler[0]
        yield
    finally:
        if oldsiginthandler:
            signal.signal(signal.SIGINT, oldsiginthandler[0])
        if shouldbail:
            raise KeyboardInterrupt


if pycompat.iswindows:
    # no fork on Windows, but we can create a detached process
    # https://msdn.microsoft.com/en-us/library/windows/desktop/ms684863.aspx
    # No stdlib constant exists for this value
    DETACHED_PROCESS = 0x00000008
    # Following creation flags might create a console GUI window.
    # Using subprocess.CREATE_NEW_CONSOLE might helps.
    # See https://phab.mercurial-scm.org/D1701 for discussion
    _creationflags = (
        DETACHED_PROCESS
        | subprocess.CREATE_NEW_PROCESS_GROUP  # pytype: disable=module-attr
    )

    def runbgcommand(
        script,
        env,
        shell=False,
        stdout=None,
        stderr=None,
        ensurestart=True,
        record_wait=None,
    ):
        '''Spawn a command without waiting for it to finish.'''
        # we can't use close_fds *and* redirect stdin. I'm not sure that we
        # need to because the detached process has no console connection.
        p = subprocess.Popen(
            tonativestr(script),
            shell=shell,
            env=tonativeenv(env),
            close_fds=True,
            creationflags=_creationflags,
            stdout=stdout,
            stderr=stderr,
        )
        if record_wait is not None:
            record_wait(p.wait)


else:

    def runbgcommand(
        cmd,
        env,
        shell=False,
        stdout=None,
        stderr=None,
        ensurestart=True,
        record_wait=None,
    ):
        '''Spawn a command without waiting for it to finish.


        When `record_wait` is not None, the spawned process will not be fully
        detached and the `record_wait` argument will be called with a the
        `Subprocess.wait` function for the spawned process.  This is mostly
        useful for developers that need to make sure the spawned process
        finished before a certain point. (eg: writing test)'''
        if pycompat.isdarwin:
            # avoid crash in CoreFoundation in case another thread
            # calls gui() while we're calling fork().
            gui()

        # double-fork to completely detach from the parent process
        # based on http://code.activestate.com/recipes/278731
        if record_wait is None:
            pid = os.fork()
            if pid:
                if not ensurestart:
                    return
                # Parent process
                (_pid, status) = os.waitpid(pid, 0)
                if os.WIFEXITED(status):
                    returncode = os.WEXITSTATUS(status)
                else:
                    returncode = -(os.WTERMSIG(status))
                if returncode != 0:
                    # The child process's return code is 0 on success, an errno
                    # value on failure, or 255 if we don't have a valid errno
                    # value.
                    #
                    # (It would be slightly nicer to return the full exception info
                    # over a pipe as the subprocess module does.  For now it
                    # doesn't seem worth adding that complexity here, though.)
                    if returncode == 255:
                        returncode = errno.EINVAL
                    raise OSError(
                        returncode,
                        b'error running %r: %s'
                        % (cmd, os.strerror(returncode)),
                    )
                return

        returncode = 255
        try:
            if record_wait is None:
                # Start a new session
                os.setsid()

            stdin = open(os.devnull, b'r')
            if stdout is None:
                stdout = open(os.devnull, b'w')
            if stderr is None:
                stderr = open(os.devnull, b'w')

            # connect stdin to devnull to make sure the subprocess can't
            # muck up that stream for mercurial.
            p = subprocess.Popen(
                cmd,
                shell=shell,
                env=env,
                close_fds=True,
                stdin=stdin,
                stdout=stdout,
                stderr=stderr,
            )
            if record_wait is not None:
                record_wait(p.wait)
            returncode = 0
        except EnvironmentError as ex:
            returncode = ex.errno & 0xFF
            if returncode == 0:
                # This shouldn't happen, but just in case make sure the
                # return code is never 0 here.
                returncode = 255
        except Exception:
            returncode = 255
        finally:
            # mission accomplished, this child needs to exit and not
            # continue the hg process here.
            if record_wait is None:
                os._exit(returncode)
