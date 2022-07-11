"""
   Deprecated PySNMP 1.x compatibility interface to exception classes.
   Suggested by Case Van Horsen <case@ironwater.com>.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp import error

class PySNMPError(error.PySnmpError):
    """Base class for PySNMP error handlers
    """
    pass

#
# Generic errors
#

class BadArgument (PySNMPError):
    """Bad argument passed
    """
    pass

#
# BER errors
#

class BEREngineError (PySNMPError):
    """Base class for BER encapsulation exceptions
    """
    pass

class UnknownTag (BEREngineError):
    """Unknown BER tag
    """
    pass

class BadEncoding (BEREngineError):
    """Incorrect BER encoding
    """
    pass

class BadObjectID (BEREngineError):
    """Malformed Object ID
    """
    pass

class BadSubObjectID (BEREngineError):
    """Bad sub-Object ID
    """
    pass

class BadIPAddress (BEREngineError):
    """Bad IP address
    """
    pass

class TypeMismatch (BEREngineError):
    """ASN.1 data type mistmatch
    """
    pass

class OverFlow (BEREngineError):
    """Data item does not fit the packet
    """
    pass

#
# SNMP engine errors
#

class SNMPEngineError (PySNMPError):
    """Base class for SNMP engine exceptions
    """
    pass

class NotConnected (SNMPEngineError):
    """SNMP session is not established
    """
    pass

class NoResponse (SNMPEngineError):
    """No SNMP response arrived before timeout
    """
    pass

class BadVersion (SNMPEngineError):
    """Unsupported SNMP version
    """
    pass

class BadCommunity (SNMPEngineError):
    """Bad SNMP community name
    """
    pass

class BadRequestID (SNMPEngineError):
    """SNMP request/response IDs mismatched
    """
    pass

class EmptyResponse (SNMPEngineError):
    """Empty SNMP response
    """
    pass

class BadPDUType (SNMPEngineError):
    """Bad SNMP PDU type
    """
    pass

class TransportError (SNMPEngineError):
    """Network transport error
    """
    def __init__ (self, why):
        self.why = why

    def __str__ (self):
        return '%s' % self.why
    
#
# SNMP errors
#

class SNMPError(PySNMPError):
    """RFC 1157 SNMP errors
    """
    # Taken from UCD SNMP code
    errors = [
        '(noError) No Error',
        '(tooBig) Response message would have been too large.',
        '(noSuchName) There is no such variable name in this MIB.',
        '(badValue) The value given has the wrong type or length.',
        '(readOnly) The two parties used do not have access to use the specified SNMP PDU.',
        '(genError) A general failure occured.',
        # The rest is unlikely to ever be reported by a v.1 agent
        '(noAccess) Access denied.',
        '(wrongType) Wrong BER type',
        '(wrongLength) Wrong BER length.',
        '(wrongEncoding) Wrong BER encoding.',
        '(wrongValue) Wrong value.',
        '(noCreation) ',
        '(inconsistentValue) ',
        '(resourceUnavailable) ',
        '(commitFailed) ',
        '(undoFailed) ',
        '(authorizationError) ',
        '(notWritable) ',
        '(inconsistentName) '
    ]
    
    def __init__ (self, status, index):
        self.status = status
        self.index = index

    def __str__ (self):
        """Return verbose error message if known
        """
        if self.status > 0 and self.status < len(self.errors):
            return self.errors[self.status]
