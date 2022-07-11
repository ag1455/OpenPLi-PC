"""
   An implementation of high-level API to SNMP v.2c message PDU objects
   (RFC1905).

   Copyright 1999-2004 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequestPduMixIn', 'GetNextRequestPduMixIn',
            'SetRequestPduMixIn', 'ResponsePduMixIn',
            'GetBulkRequestPduMixIn', 'InformRequestPduMixIn',
            'ReportPduMixIn', 'SnmpV2TrapPduMixIn', 'registerMixIns' ]

from pysnmp.proto import rfc1902, rfc1905
from pysnmp.proto.api.generic import rfc1157
import pysnmp.proto.api.alpha

class RequestPduMixIn(rfc1157.RequestPduMixIn):
    def apiGenSetVarBind(self, varBinds):
        tempVarBinds = []
        for oid, val in varBinds:
            if val is None: val = rfc1902.Null()
            tempVarBinds.append((oid, val))
        apply(self.apiAlphaSetVarBindList, tempVarBinds)

# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass
class InformRequestPduMixIn(RequestPduMixIn): pass
class ReportPduMixIn(RequestPduMixIn): pass
class SnmpV2TrapPduMixIn(RequestPduMixIn): pass

class ResponsePduMixIn(rfc1157.GetResponsePduMixIn): pass

# A v1-style alias
GetResponsePduMixIn = ResponsePduMixIn
    
class GetBulkRequestPduMixIn(RequestPduMixIn):
    def apiGenGetNonRepeaters(self): return self.apiAlphaGetNonRepeaters().get()
    def apiGenSetNonRepeaters(self, value): self.apiAlphaSetNonRepeaters(value)
    def apiGenGetMaxRepetitions(self): return self.apiAlphaGetMaxRepetitions().get()
    def apiGenSetMaxRepetitions(self, value): self.apiAlphaSetMaxRepetitions(value)

class MessageMixIn(rfc1157.MessageMixIn): pass

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1905.GetRequestPdu, GetRequestPduMixIn),
                   (rfc1905.GetNextRequestPdu, GetNextRequestPduMixIn),
                   (rfc1905.SetRequestPdu, SetRequestPduMixIn),
                   (rfc1905.ResponsePdu, ResponsePduMixIn),
                   (rfc1905.GetBulkRequestPdu, GetBulkRequestPduMixIn),
                   (rfc1905.InformRequestPdu, InformRequestPduMixIn),
                   (rfc1905.ReportPdu, ReportPduMixIn),
                   (rfc1905.SnmpV2TrapPdu, SnmpV2TrapPduMixIn),
                   (rfc1905.Message, MessageMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
