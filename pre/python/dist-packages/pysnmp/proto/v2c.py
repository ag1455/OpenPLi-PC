"""
   Implementation of SMI and SNMP for v.2c (RFC1902 & RFC1905)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequest', 'GetNextRequest', 'SetRequest', 'Response', \
            'GetBulkRequest', 'InformRequest', 'Report', 'SnmpV2Trap',
            'Request' ]

from pysnmp.proto.rfc1902 import *
from pysnmp.proto import rfc1905, error
from pysnmp.asn1 import constraints

# These do not require any additional subtyping
from rfc1905 import BindValue, VarBind, VarBindList, NoSuchObject, \
     NoSuchInstance, EndOfMibView

class _RequestPduSpecifics:
    """Request PDU specific
    """
    class ErrorStatus(rfc1905.ErrorStatus):
        """Request-specific PDU error status
        """
        constraints = (
            constraints.ValueRangeConstraint(0, 0),
        )

    class ErrorIndex(rfc1905.ErrorIndex):
        """Request-specific PDU error index
        """
        constraints = (
            constraints.ValueRangeConstraint(0, 0),
        )

    def reply(self, **kwargs):
        """Build and return a response PDU from this request PDU
        """
        rsp = apply(Response.Pdus.ResponsePdu, [], kwargs)
        rsp['request_id'] = self['request_id']
        rsp['variable_bindings'] = self['variable_bindings']

        return rsp

    def match(self, rspPdu):
        """Return true if response PDU matches request PDU
        """
        if not isinstance(rspPdu, rfc1905.ResponsePdu):
            raise error.BadArgumentError('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(rspPdu)))
        
        if self['request_id'] == rspPdu['request_id']:
            return 1

class _RequestSpecifics:
    """Request-specific methods
    """
    def reply(self, **kwargs):
        """Create v.2c RESPONSE message from this request message
        """
        rsp = apply(Response, [], kwargs)
        rsp['community'] = self['community']

        pdu = self['pdu'].values()[0]
        if hasattr(pdu, 'reply'):
            rsp['pdu']['response'] = pdu.reply()

        return rsp

    def match(self, rsp):
        """Return true if response message matches this request message
        """
        if not isinstance(rsp, Response):
            raise error.BadArgumentError('Incompatible types for comparation %s with %s' % (self.__class__.__name__, str(rsp)))

        # Make sure response matches request
        if self['community'] !=  rsp['community']:
            return
        
        return self['pdu'].values()[0].match(rsp['pdu'].values()[0])

# Get-Request

class GetRequest(rfc1905.Message, _RequestSpecifics):
    """Strictly typed v.2c GETREQUEST
    """
    class Pdus(rfc1905.Pdus):
        """GETREQUEST specific selection of applicible PDUs
        """
        class GetRequestPdu(rfc1905.GetRequestPdu, _RequestPduSpecifics):
            """Strictly typed v.2c GETREQUEST PDU class
            """
            fixedComponents = [ rfc1905.RequestId,\
                                _RequestPduSpecifics.ErrorStatus, \
                                _RequestPduSpecifics.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'get_request' ]
        choiceComponents = [ GetRequestPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]

# GetNext request

class GetNextRequest(rfc1905.Message, _RequestSpecifics):
    """Strictly typed v.2c GETNEXTREQUEST
    """
    class Pdus(rfc1905.Pdus):
        """GETNEXTREQUEST specific selection of applicible PDUs
        """
        class GetNextRequestPdu(rfc1905.GetNextRequestPdu, \
                                _RequestPduSpecifics):
            """Strictly typed v.2c GETNEXTREQUEST PDU class
            """
            fixedComponents = [ rfc1905.RequestId,\
                                _RequestPduSpecifics.ErrorStatus, \
                                _RequestPduSpecifics.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'get_next_request' ]
        choiceComponents = [ GetNextRequestPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]

# Set request

class SetRequest(rfc1905.Message, _RequestSpecifics):
    """Strictly typed v.2c SETREQUEST
    """
    class Community(rfc1905.Community):
        """SETREQUEST specific community name
        """
        initialValue = 'private'
    
    class Pdus(rfc1905.Pdus):
        """SETREQUEST specific selection of applicible PDUs
        """
        class SetRequestPdu(rfc1905.SetRequestPdu, _RequestPduSpecifics):
            """Strictly typed v.2c SETREQUEST PDU class
            """
            fixedComponents = [ rfc1905.RequestId,\
                                _RequestPduSpecifics.ErrorStatus, \
                                _RequestPduSpecifics.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'set_request' ]
        choiceComponents = [ SetRequestPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, Community, Pdus ]

# Inform request

class InformRequest(rfc1905.Message, _RequestSpecifics):
    """Strictly typed v.2c INFORMREQUEST
    """
    class Pdus(rfc1905.Pdus):
        """INFORMREQUEST specific selection of applicible PDUs
        """
        class InformRequestPdu(rfc1905.InformRequestPdu, _RequestPduSpecifics):
            """Strictly typed v.2c INFORMREQUEST PDU class
            """
            fixedComponents = [ rfc1905.RequestId,\
                                _RequestPduSpecifics.ErrorStatus, \
                                _RequestPduSpecifics.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'inform_request' ]
        choiceComponents = [ InformRequestPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]

# SNMPv2-trap

class SnmpV2Trap(rfc1905.Message):
    """Strictly typed v.2c SNMPV2TRAP message
    """
    class Pdus(rfc1905.Pdus):
        """SNMPV2TRAP specific selection of applicible PDUs
        """
        class SnmpV2TrapPdu(rfc1905.SnmpV2TrapPdu):
            """Strictly typed v.2c SNMPV2TRAP PDU class
            """
            fixedComponents = [ rfc1905.RequestId,\
                                rfc1905.ErrorStatus, \
                                rfc1905.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'snmpV2_trap' ]
        choiceComponents = [ SnmpV2TrapPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]

# An alias to make it looking similar to v.1
Trap = SnmpV2Trap

# Report message

class Report(rfc1905.Message):
    """Strictly typed v.2c REPORT message
    """
    class Pdus(rfc1905.Pdus):
        """REPORT specific selection of applicible PDUs
        """
        class ReportPdu(rfc1905.ReportPdu, _RequestPduSpecifics):
            """Strictly typed v.2c REPORT PDU class
            """
            fixedComponents = [ rfc1905.RequestId,\
                                rfc1905.ErrorStatus, \
                                rfc1905.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'report' ]
        choiceComponents = [ ReportPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]

# GetBulk request

class GetBulkRequest(rfc1905.Message, _RequestSpecifics):
    """Strictly typed v.2c GetBulkRequest
    """
    class Pdus(rfc1905.Pdus):
        """GetBulkRequest specific selection of applicible PDUs
        """
        class GetBulkRequestPdu(rfc1905.GetBulkRequestPdu,\
                                _RequestPduSpecifics):
            """Strictly typed v.2c GetBulkRequest PDU class
            """
            fixedComponents = [ rfc1905.RequestId, rfc1905.NonRepeaters, \
                                rfc1905.MaxRepetitions, VarBindList ]

            def reply(self, **kwargs):
                """Build a response message from GetBulk request (w/o bindings)
                """
                rsp = apply(Response.Pdus.ResponsePdu, [], kwargs)
                rsp['request_id'] = self['request_id']
                return rsp
            
        choiceNames = [ 'get_bulk_request' ]
        choiceComponents = [ GetBulkRequestPdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]

# Response

class Response(rfc1905.Message):
    """Strictly typed v.2c GETREQUEST
    """
    class Pdus(rfc1905.Pdus):
        """Response specific selection of applicible PDUs
        """
        class ResponsePdu(rfc1905.ResponsePdu):
            """Strictly typed v.2c Response PDU class
            """
            fixedComponents = [ rfc1905.RequestId,\
                                rfc1905.ErrorStatus, \
                                rfc1905.ErrorIndex, \
                                VarBindList ]

        choiceNames = [ 'response' ]
        choiceComponents = [ ResponsePdu ]
        initialComponent = choiceComponents[0]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]

# An alias to make it looking similar to v.1
GetResponse = Response

# Requests demux

class Request(rfc1905.Message, _RequestSpecifics):
    """Strictly typed any v.2c request
    """
    class Pdus(rfc1905.Pdus):
        """Request specific selection of applicible PDUs
        """
        choiceNames = [ 'get_request', 'get_next_request', \
                        'get_bulk_request', 'set_request', 'inform_request' ]
        choiceComponents = [ GetRequest.Pdus.GetRequestPdu, \
                             GetNextRequest.Pdus.GetNextRequestPdu, \
                             GetBulkRequest.Pdus.GetBulkRequestPdu, \
                             SetRequest.Pdus.SetRequestPdu, \
                             InformRequest.Pdus.InformRequestPdu ]

    fixedComponents = [ rfc1905.Version, rfc1905.Community, Pdus ]
