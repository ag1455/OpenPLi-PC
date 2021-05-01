"""
   An implementation of high-level API to SNMP v.1 message PDU objects
   (RFC1157).

   Copyright 1999-2004 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequestPduMixIn', 'GetNextRequestPduMixIn',
            'SetRequestPduMixIn', 'GetResponsePduMixIn',
            'ResponsePduMixIn', 'TrapPduMixIn', 'MessageMixIn',
            'registerMixIns' ]

import pysnmp.proto.api.alpha.rfc1157
from pysnmp.proto import rfc1155, rfc1157

class RequestPduMixIn:
    def apiGenGetRequestId(self): return self.apiAlphaGetRequestId().get()
    def apiGenSetRequestId(self, value): self.apiAlphaSetRequestId(value)
    def apiGenGetVarBind(self):
        return map(lambda x: (x[0].get(), x[1]), \
                   map(lambda x: x.apiAlphaGetOidVal(), \
                       self.apiAlphaGetVarBindList()))
    def apiGenSetVarBind(self, varBinds):
        tempVarBinds = []
        for oid, val in varBinds:
            if val is None: val = rfc1155.Null()
            tempVarBinds.append((oid, val))
        apply(self.apiAlphaSetVarBindList, tempVarBinds)
    
# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass

class GetResponsePduMixIn(RequestPduMixIn):
    def apiGenGetErrorStatus(self): return self.apiAlphaGetErrorStatus().get()
    def apiGenSetErrorStatus(self, value): self.apiAlphaSetErrorStatus(value)
    def apiGenGetErrorIndex(self): return self.apiAlphaGetErrorIndex().get()
    def apiGenSetErrorIndex(self, value): self.apiAlphaSetErrorIndex(value)

# A v2c-style alias
ResponsePduMixIn = GetResponsePduMixIn

class TrapPduMixIn(RequestPduMixIn):
    def apiGenGetEnterprise(self): return self.apiAlphaGetEnterprise().get()
    def apiGenSetEnterprise(self, value): self.apiAlphaSetEnterprise(value)
    def apiGenGetAgentAddr(self): return self.apiAlphaGetAgentAddr().get()
    def apiGenSetAgentAddr(self, value): self.apiAlphaSetAgentAddr(value)
    def apiGenGetGenericTrap(self): return self.apiAlphaGetGenericTrap().get()
    def apiGenSetGenericTrap(self, value): self.apiAlphaSetGenericTrap(value)
    def apiGenGetSpecificTrap(self): return self.apiAlphaGetSpecificTrap().get()
    def apiGenSetSpecificTrap(self, value): self.apiAlphaSetSpecificTrap(value)
    def apiGenGetTimeStamp(self): return self.apiAlphaGetTimeStamp().get()
    def apiGenSetTimeStamp(self, value): self.apiAlphaSetTimeStamp(value)

class MessageMixIn:
    def apiGenGetVersion(self): return self.apiAlphaGetVersion().get()
    def apiGenGetCommunity(self): return self.apiAlphaGetCommunity().get()
    def apiGenSetCommunity(self, value): self.apiAlphaSetCommunity(value)
    def apiGenGetPdu(self): return self.apiAlphaGetPdu()
    def apiGenSetPdu(self, value): self.apiAlphaSetPdu(value)

def mixIn():
    """Register this module's mix-in classes at their bases
    """
    mixInComps = [ (rfc1157.GetRequestPdu, GetRequestPduMixIn),
                   (rfc1157.GetNextRequestPdu, GetNextRequestPduMixIn),
                   (rfc1157.SetRequestPdu, SetRequestPduMixIn),
                   (rfc1157.GetResponsePdu, GetResponsePduMixIn),
                   (rfc1157.TrapPdu, TrapPduMixIn),
                   (rfc1157.Message, MessageMixIn) ]

    for (baseClass, mixIn) in mixInComps:
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
