# -*- coding: utf-8 -*-

import sys
import threading
import functools
import contextlib
import click

from ._compat import reraise

try:
    import queue
except ImportError:
    import Queue as queue

# The docs state that "Future should not be instantiated directly, only by
# Executors", but since I'm basically implementing my own executor here, I
# think we're fine.
try:
    from concurrent.futures import Future as _Future
except ImportError:
    from futures import Future as _Future

__version__ = '0.4.4'

_CTX_WORKER_KEY = __name__ + '.uiworker'


def _is_main_thread(thread=None):
    thread = thread or threading.current_thread()
    return type(thread).__name__ == '_MainThread'


class Thread(threading.Thread):
    '''A thread that automatically pushes the parent thread's context in the
    new thread.

    Since version 5.0, click maintains global stacks of context objects. The
    topmost context on that stack can be accessed with
    :py:func:`get_current_context`.

    There is one stack for each Python thread. That means if you are in the
    main thread (where you can use :py:func:`get_current_context` just fine)
    and spawn a :py:class:`threading.Thread`, that thread won't be able to
    access the same context using :py:func:`get_current_context`.

    :py:class:`Thread` is a subclass of :py:class:`threading.Thread` that
    preserves the current thread context when spawning a new one, by pushing it
    on the stack of the new thread as well.
    '''

    def __init__(self, *args, **kwargs):
        self._click_context = click.get_current_context()
        super(Thread, self).__init__(*args, **kwargs)

    def run(self):
        with self._click_context:
            return super(Thread, self).run()


class UiWorker(object):
    '''
    A worker-queue system to manage and synchronize output and prompts from
    other threads.

    >>> import click
    >>> from click_threading import UiWorker, Thread, get_ui_worker
    >>> ui = UiWorker()  # on main thread
    >>> def target():
    ...     click.echo("Hello world!")
    ...     get_ui_worker().shutdown()
    ...
    >>>
    >>> @click.command()
    ... def cli():
    ...     with ui.patch_click():
    ...         t = Thread(target=target)
    ...         t.start()
    ...         ui.run()
    >>> runner = click.testing.CliRunner()
    >>> result = runner.invoke(cli, [])
    >>> assert result.output.strip() == 'Hello world!'

    Using this class instead of just spawning threads brings a few advantages:

    - If one thread prompts for input, other output from other threads is
      queued until the :py:func:`click.prompt` call returns.
    - If you call echo with a multiline-string, it is guaranteed that this
      string is not interleaved with other output.

    Disadvantages:

    - The main thread is used for the output (using any other thread produces
      weird behavior with interrupts). ``ui.run()`` in the above example blocks
      until ``ui.shutdown()`` is called.
    '''
    SHUTDOWN = object()

    def __init__(self):
        if not _is_main_thread():
            raise RuntimeError('The UiWorker can only run on the main thread.')

        self.tasks = queue.Queue()

    def shutdown(self):
        self.put(self.SHUTDOWN, wait=False)

    def run(self):
        while True:
            func, future = self.tasks.get()
            if func is self.SHUTDOWN:
                return

            try:
                result = func()
            except BaseException as e:
                future.set_exception(e)
            else:
                future.set_result(result)

    def put(self, func, wait=True):
        if _is_main_thread():
            return func()

        future = _Future()
        self.tasks.put((func, future))
        if not wait:
            return

        return future.result()

    @contextlib.contextmanager
    def patch_click(self):
        from .monkey import patch_ui_functions

        def wrapper(f, info):
            @functools.wraps(f)
            def inner(*a, **kw):
                return get_ui_worker() \
                    .put(lambda: f(*a, **kw), wait=info.interactive)
            return inner

        ctx = click.get_current_context()
        with patch_ui_functions(wrapper):
            ctx.meta[_CTX_WORKER_KEY] = self
            try:
                yield
            finally:
                assert ctx.meta.pop(_CTX_WORKER_KEY) is self


def get_ui_worker():
    try:
        ctx = click.get_current_context()
        return ctx.meta[_CTX_WORKER_KEY]
    except (RuntimeError, KeyError):
        raise RuntimeError('UI worker not found.')
