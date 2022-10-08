# -*- coding: utf-8 -*-

import inspect
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    getargspec = inspect.getargspec
    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')
else:
    getargspec = inspect.getfullargspec
    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value
