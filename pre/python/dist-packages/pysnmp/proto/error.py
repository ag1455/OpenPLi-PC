"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002.
"""   
from pysnmp import error

class ProtoError(error.PySnmpError):
    """Base class for snmp sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(ProtoError):
    """Malformed argument
    """
    pass

class NotImplementedError(ProtoError):
    """Feature not implemented
    """
    pass

# SNMP v3 exceptions

class SnmpV3Error(ProtoError):
    """SNMPv3 specific exceptions
    """
    pass

class CacheExpiredError(SnmpV3Error):
    """Request information (rfc3412) cache expired
    """
    pass

class InternalError(SnmpV3Error):
    """SNMP v.3 engine error
    """
    pass

class MessageProcessingError(SnmpV3Error):
    """Illegal message params
    """

class CacheExpiredError(SnmpV3Error):
    """Request information (rfc3412) cache expired
    """
    pass
