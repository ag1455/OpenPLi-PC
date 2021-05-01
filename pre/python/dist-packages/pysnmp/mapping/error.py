"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002.
"""   
from pysnmp import error

class TransportError(error.PySnmpError):
    """Base class for transport related exceptions
    """
    pass
