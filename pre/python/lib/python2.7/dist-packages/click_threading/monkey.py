# -*- coding: utf-8 -*-

import types
import contextlib
import inspect

from ._compat import PY2, getargspec


class FunctionInfo(object):
    def __init__(self, interactive):
        self.interactive = interactive


_ui_functions = {
    'echo_via_pager': FunctionInfo(interactive=True),
    'prompt': FunctionInfo(interactive=True),
    'confirm': FunctionInfo(interactive=True),
    'clear': FunctionInfo(interactive=False),
    'echo': FunctionInfo(interactive=False),
    'edit': FunctionInfo(interactive=True),
    'launch': FunctionInfo(interactive=True),
    'getchar': FunctionInfo(interactive=True),
    'pause': FunctionInfo(interactive=True),
}


@contextlib.contextmanager
def patch_ui_functions(wrapper):
    '''Wrap all termui functions with a custom decorator.'''
    NONE = object()
    import click

    saved = []

    for name, info in sorted(_ui_functions.items()):
        f = getattr(click, name, NONE)
        if f is NONE:
            continue

        new_f = wrapper(_copy_fn(f), info)

        argspec = getargspec(f)
        signature = inspect.formatargspec(*argspec) \
            .lstrip('(') \
            .rstrip(')')
        args = ', '.join(arg.split('=')[0].split(':')[0].strip()
                         for arg in signature.split(','))

        stub_f = eval('lambda {s}: {n}._real_click_fn({a})'
                      .format(n=f.__name__, s=signature, a=args))

        if PY2:
            saved.append((f, f.func_code))
            f.func_code = stub_f.func_code
        else:
            saved.append((f, f.__code__))
            f.__code__ = stub_f.__code__

        f._real_click_fn = new_f

    try:
        yield
    finally:
        for f, code in saved:
            if PY2:
                f.func_code = code
            else:
                f.__code__ = code

            del f._real_click_fn


def _copy_fn(f):
    if PY2:
        return types.FunctionType(f.func_code, f.func_globals, f.func_name,
                                  f.func_defaults, f.func_closure)
    else:
        return types.FunctionType(f.__code__, f.__globals__, f.__name__,
                                  f.__defaults__, f.__closure__)
