"""Top-level exception class
"""   
from exceptions import Exception

class PySnmpError(Exception):
    def __init__(self, why=''):
        Exception.__init__(self)
        self.why = str(why)

    def __str__(self): return self.why
    def __repr__(self): return self.__class__.__name__ + '(' + self.why + ')'
    def __nonzero__(self):
        if len(self.why): return 1
        else: return 0

class PySnmpVersionError(PySnmpError): pass
