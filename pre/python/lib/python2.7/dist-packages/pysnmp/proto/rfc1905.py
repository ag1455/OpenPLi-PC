"""
   Implementation of SNMP v.2c (RFC1905)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'Version', 'Community', 'RequestId', 'NoSuchObject', \
            'NoSuchInstance', 'EndOfMibView', 'BindValue', 'VarBind', \
            'VarBindList', 'Pdu', 'NonRepeaters', 'MaxRepetitions', \
            'GetRequestPdu', 'GetNextRequestPdu', 'ResponsePdu', \
            'SetRequestPdu', 'GetBulkRequestPdu', 'InformRequestPdu', \
            'SnmpV2TrapPdu', 'ReportPdu', 'Pdus', 'Message' ]

from time import time
from pysnmp.asn1.base import tagClasses
from pysnmp.proto import rfc1902
from pysnmp.proto.rfc1157 import InitialRequestIdMixIn
import pysnmp.asn1.error
from pysnmp.asn1 import constraints

# Value reference -- max bindings in VarBindList
max_bindings = rfc1902.Integer(2147483647)

class Version(rfc1902.Integer):
    """Message version
    """
    constraints=(
        constraints.SingleValueConstraint( 1 ),
    )
    initialValue = 1
    
class Community(rfc1902.OctetString):
    """Community name
    """
    initialValue = 'public'    

class RequestId(InitialRequestIdMixIn, rfc1902.Integer):
    """Request ID
    """
    pass

class ErrorStatus(rfc1902.Integer):
    """Error status
    """
    initialValue = 0
    constraints = (
        constraints.ValueRangeConstraint(0, 18),
    )
    pduErrors = [ '(noError) No Error',
                  '(tooBig) Response message would have been too large',
                  '(noSuchName) There is no such variable name in this MIB',
                  '(badValue) The value given has the wrong type or length',
                  '(readOnly) No modifications allowed to this object',
                  '(genError) A general failure occured',
                  '(noAccess) Access denied',
                  '(wrongType) Wrong BER type',
                  '(wrongLength) Wrong BER length',
                  '(wrongEncoding) Wrong BER encoding',
                  '(wrongValue) Wrong value',
                  '(noCreation) Object creation prohibited',
                  '(inconsistentValue) Inconsistent value',
                  '(resourceUnavailable) Resource unavailable',
                  '(commitFailed) Commit failed',
                  '(undoFailed) Undo failed',
                  '(authorizationError) Authorization error',
                  '(notWritable) Object is not writable',
                  '(inconsistentName) Inconsistent object name' ]

    def __str__(self):
        """Return verbose error message if known
        """
        return '%s: %d (%s)' % (self.__class__.__name__, self.get(),
                                self.pduErrors[self.get()])
    
class ErrorIndex(rfc1902.Integer):
    """Error index
    """
    constraints = (
        constraints.ValueRangeConstraint(0, max_bindings),
    )

class NoSuchObject(rfc1902.Null):
    """noSuchObject exception
    """
    # Implicit tagging
    tagClass = tagClasses['CONTEXT']
    tagId = 0x00

class NoSuchInstance(rfc1902.Null):
    """noSuchInstance exception
    """
    # Implicit tagging
    tagClass = tagClasses['CONTEXT']
    tagId = 0x01

class EndOfMibView(rfc1902.Null):
    """endOfMibView exception
    """
    # Implicit tagging
    tagClass = tagClasses['CONTEXT']
    tagId = 0x02

class BindValue(rfc1902.Choice):
    """Binding value
    """
    choiceNames = ['value', 'unspecified', 'noSuchObject', 'noSuchInstance',\
                   'endOfMibView']
    choiceComponents = [ rfc1902.ObjectSyntax, rfc1902.Null, \
                         NoSuchObject, NoSuchInstance, EndOfMibView ]
    initialComponent = rfc1902.Null
    
class VarBind(rfc1902.Sequence):
    """Variable binding
    """
    # Bind structure
    fixedNames = [ 'name', 'value' ]
    fixedComponents = [ rfc1902.ObjectName, BindValue ]

class VarBindList(rfc1902.SequenceOf):
    """List of variable bindings
    """
    protoComponent = VarBind
    constraints = (
        constraints.ValueSizeConstraint( 0,max_bindings ),
    )
    
class Pdu(rfc1902.Sequence):
    """Base class for a non-bulk PDU
    """
    # Tag class implicitly
    tagClass = tagClasses['CONTEXT']

    # PDU structure
    fixedNames = [ 'request_id', 'error_status', 'error_index', \
                   'variable_bindings' ]
    fixedComponents = [ RequestId, ErrorStatus, ErrorIndex, \
                        VarBindList ]

class NonRepeaters(rfc1902.Integer):
    """Bulk PDU non-repeaters
    """
    constraints = (
        constraints.ValueRangeConstraint(0, max_bindings),
    )

class MaxRepetitions(rfc1902.Integer):
    """Bulk PDU max-repetitions
    """
    constraints = (
        constraints.ValueRangeConstraint(0, max_bindings),
    )
    initialValue = 255
    
class BulkPdu(rfc1902.Sequence):
    """Base class for bulk PDU
    """
    # Tag class implicitly
    tagClass = tagClasses['CONTEXT']

    # PDU structure
    fixedNames = [ 'request_id', 'non_repeaters', 'max_repetitions', \
                   'variable_bindings' ]
    fixedComponents = [ RequestId, NonRepeaters, MaxRepetitions, \
                        VarBindList ]

class GetRequestPdu(Pdu):
    """The GetRequest-PDU
    """
    # Implicit tagging
    tagId = 0x00

class GetNextRequestPdu(Pdu):
    """The GetNextRequest-PDU
    """
    # Implicit tagging
    tagId = 0x01

class ResponsePdu(Pdu):
    """The GetResponse-PDU
    """
    # Implicit tagging
    tagId = 0x02

class SetRequestPdu(Pdu):
    """The SetRequest-PDU
    """
    # Implicit tagging
    tagId = 0x03

class GetBulkRequestPdu(BulkPdu):
    """The GetBulkRequestPdu-PDU
    """
    # Implicit tagging
    tagId = 0x05

class InformRequestPdu(Pdu):
    """The InformRequest-PDU
    """
    # Implicit tagging
    tagId = 0x06

class SnmpV2TrapPdu(Pdu):
    """The SNMPv2Trap-PDU
    """
    # Implicit tagging
    tagId = 0x07

# XXX v1 compatible alias
TrapPdu = SnmpV2TrapPdu

class ReportPdu(Pdu):
    """The Report-PDU
    """
    # Implicit tagging
    tagId = 0x08

class Pdus(rfc1902.Choice):
    """
    """
    choiceNames = [ 'get_request', 'get_next_request', 'get_bulk_request', \
                    'response', 'set_request', 'inform_request', \
                    'snmpV2_trap', 'report' ]
    choiceComponents = [ GetRequestPdu, GetNextRequestPdu, GetBulkRequestPdu,\
                         ResponsePdu, SetRequestPdu, InformRequestPdu, \
                         SnmpV2TrapPdu, ReportPdu ]
    
class Message(rfc1902.Sequence):
    """Top level message
    """
    fixedNames = [ 'version', 'community', 'pdu' ]
    fixedComponents = [ Version, Community, Pdus ]

def probeMessageVersion(wholeMsg):
    class MessageHead(Message):
        fixedNames = [ 'version' ]
        fixedComponents = [ rfc1902.Integer ]

    msg = MessageHead()
    msg.decode(wholeMsg)
    if msg['version'] == Version():
        return 1
