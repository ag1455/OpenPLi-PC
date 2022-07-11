"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002.
"""   
from pysnmp.mapping import error

class SnmpOverUdpError(error.TransportError):
    """Base class for snmp over UDP sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(SnmpOverUdpError):
    """Malformed argument
    """
    pass

class NetworkError(SnmpOverUdpError):
    """Network error
    """
    pass

class NoResponseError(NetworkError):
    """No response arrived before timeout
    """
    pass

class IdleTimeoutError(NetworkError):
    """No request arrived before timeout
    """
    pass
