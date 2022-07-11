"""
   Implementation of SNMP v.1 (RFC1157)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'Version', 'Community', 'RequestId', 'ErrorStatus', 'ErrorIndex',\
            'VarBind', 'VarBindList', 'GetRequestPdu', 'GetNextRequestPdu',\
            'GetResponsePdu', 'SetRequestPdu', 'Enterprise', 'AgentAddr',\
            'GenericTrap', 'SpecificTrap', 'TimeStamp', 'TrapPdu', 'Pdus',\
            'Message' ]

from time import time
from pysnmp.asn1.base import tagClasses
from pysnmp.proto import rfc1155, error
from pysnmp.asn1 import constraints
import pysnmp.asn1.error

class Version(rfc1155.Integer):
    """Message version
    """
    constraints=(
        constraints.SingleValueConstraint( 0 ),
    )
    initialValue = 0
    
class Community(rfc1155.OctetString):
    """Community name
    """
    initialValue = 'public'

globalRequestId = 1000 - long(time() / 100 % 1 * 1000)

class InitialRequestIdMixIn:
    def initialValue(self):
        global globalRequestId
        try:
            self.set(globalRequestId)
        except pysnmp.asn1.error.ValueConstraintError:
            globalRequestId = 0L
            self.set(globalRequestId)
        else:
            globalRequestId = globalRequestId + 1
            
class RequestId(InitialRequestIdMixIn, rfc1155.Integer):
    """Request ID
    """
    pass
    
class ErrorStatus(rfc1155.Integer):
    """Error status
    """
    initialValue = 0
    constraints = (
        constraints.ValueRangeConstraint(0, 5),
    )
    pduErrors = [ '(noError) No Error',
                  '(tooBig) Response message would have been too large',
                  '(noSuchName) There is no such variable name in this MIB',
                  '(badValue) The value given has the wrong type or length',
                  '(readOnly) No modifications allowed to this object',
                  '(genError) A general failure occured' ]
    
    def __str__(self):
        """Return verbose error message if known
        """
        return '%s: %d (%s)' % (self.__class__.__name__, self.get(),
                                self.pduErrors[self.get()])

class ErrorIndex(rfc1155.Integer):
    """Error index
    """
    initialValue = 0

class VarBind(rfc1155.Sequence):
    """Variable binding
    """
    # Bind structure
    fixedNames = [ 'name', 'value' ]
    fixedComponents = [ rfc1155.ObjectName, rfc1155.ObjectSyntax ]
        
class VarBindList(rfc1155.SequenceOf):
    """List of variable bindings
    """
    protoComponent = VarBind
    
class RequestPdu(rfc1155.Sequence):
    """Base class for a non-trap PDU
    """
    # Tag class implicitly
    tagClass = tagClasses['CONTEXT']

    # PDU structure
    fixedNames = [ 'request_id', 'error_status', 'error_index', \
                   'variable_bindings' ]
    fixedComponents = [ RequestId, ErrorStatus, ErrorIndex, \
                        VarBindList ]

class GetRequestPdu(RequestPdu):
    """The GetRequest-PDU
    """
    # Implicit tagging
    tagId = 0x00

class GetNextRequestPdu(RequestPdu):
    """The GetNextRequest-PDU
    """
    # Implicit tagging
    tagId = 0x01

class GetResponsePdu(RequestPdu):
    """The GetResponse-PDU
    """
    # Implicit tagging
    tagId = 0x02

class SetRequestPdu(RequestPdu):
    """The SetRequest-PDU
    """
    # Implicit tagging
    tagId = 0x03

# Trap stuff

class Enterprise(rfc1155.ObjectIdentifier):
    """Trap PDU enterprise Object ID
    """
    initialValue = '1.3.6.1.1.2.3.4.1'

class AgentAddr(rfc1155.NetworkAddress):
    """Trap PDU agent address
    """
    pass

class GenericTrap(rfc1155.Integer):
    """Trap PDU generic trap
    """
    initialValue = 0
    constraints = (
        constraints.ValueRangeConstraint(0, 6),
    )
    verboseTraps = [ 'coldStart', 'warmStart', 'linkDown', 'linkUp', \
                     'authenticationFailure', 'egpNeighborLoss', \
                     'enterpriseSpecific' ]

    def __str__(self):
        """Return verbose error message if known
        """
        return '%s: %d (%s)' % (self.__class__.__name__, self.get(),
                           self.verboseTraps[self.get()])

class SpecificTrap(rfc1155.Integer):
    """Trap PDU specific trap
    """
    initialValue = 0

class TimeStamp(rfc1155.TimeTicks):
    """Trap PDU time stamp
    """
    def __init__(self, value=int(time())):
        """Set current time by default
        """
        rfc1155.TimeTicks.__init__(self, value)

class TrapPdu(rfc1155.Sequence):
    """Trap PDU
    """
    # Tag class implicitly
    tagClass = tagClasses['CONTEXT']
    tagId = 0x04

    # PDU structure
    fixedNames = [ 'enterprise', 'agent_addr', 'generic_trap', \
                   'specific_trap', 'time_stamp', 'variable_bindings' ]
    fixedComponents = [ Enterprise, AgentAddr, GenericTrap, \
                        SpecificTrap, TimeStamp, VarBindList ]

class Pdus(rfc1155.Choice):
    """The CHOICE of PDUs
    """
    choiceNames = [ 'get_request', 'get_next_request', \
                    'get_response', 'set_request', 'trap' ]
    choiceComponents = [ GetRequestPdu, GetNextRequestPdu, \
                         GetResponsePdu, SetRequestPdu, TrapPdu ]
    
class Message(rfc1155.Sequence):
    """Top level message
    """
    fixedNames = [ 'version', 'community', 'pdu' ]
    fixedComponents = [ Version, Community, Pdus ]

def probeMessageVersion(wholeMsg):
    class MessageHead(Message):
        fixedNames = [ 'version' ]
        fixedComponents = [ rfc1155.Integer ]

    msg = MessageHead()
    msg.decode(wholeMsg)
    if msg['version'] == Version():
        return 1
