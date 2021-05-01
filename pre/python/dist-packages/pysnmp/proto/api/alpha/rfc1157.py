"""An implementation of high-level API to SNMP v1 message & PDU
   objects (RFC1157)
"""
from types import InstanceType
from pysnmp.proto import rfc1157
from pysnmp.proto.api import error

class VarBindMixIn:
    def apiAlphaSetOidVal(self, (oid, val)):
        if oid is not None:
            self.apiAlphaSetSimpleComponent('name', oid)
        if val is not None:
            self['value'].apiAlphaSetTerminalValue(val)
        return self

    def apiAlphaGetOidVal(self):
        return (self['name'], self['value'].apiAlphaGetTerminalValue())

class PduMixInBase:
    def apiAlphaGetVarBindList(self): return self['variable_bindings']
    def apiAlphaSetVarBindList(self, *varBinds):
        varBindList = self['variable_bindings']
        idx = 0
        for varBind in varBinds:
            if isinstance(varBind, rfc1157.VarBind):
                varBindList[idx] = varBind
            else:
                if len(varBindList) <= idx:
                    varBindList.append(varBindList.componentFactoryBorrow())
                varBindList[idx].apiAlphaSetOidVal(varBind)
            idx = idx + 1
        del varBindList[idx:]

    def apiAlphaGetTableIndices(self, rsp, *headerVars):
        varBindList = rsp.apiAlphaGetVarBindList()
        if len(varBindList) != len(headerVars):
            raise error.BadArgumentError('Unmatching table head & row size %s vs %s' % (len(headerVars), len(varBindList)))
        if len(headerVars) == 0:
            raise error.BadArgumentError('Empty table')
        endOfMibIndices = rsp.apiAlphaGetEndOfMibIndices()
        varBindRows = []
        for idx in range(len(varBindList)):
            if idx in endOfMibIndices:
                varBindRows.append(-1)
                continue
            oid, val = varBindList[idx].apiAlphaGetOidVal()
            # XXX isaprefix rename
            if not headerVars[idx].isaprefix(oid):
                varBindRows.append(-1)
                continue
            varBindRows.append(idx)
        return [ varBindRows ]
            
class RequestPduMixIn(PduMixInBase):
    def apiAlphaGetRequestId(self): return self['request_id']
    def apiAlphaSetRequestId(self, value):
        self.apiAlphaSetSimpleComponent('request_id', value)
    def apiAlphaReply(self, pdu=None):
        """Return initialized response PDU
        """
        if pdu is None:
            pdu = rfc1157.GetResponsePdu()
        elif not isinstance(pdu, rfc1157.GetResponsePdu):
            raise error.BadArgumentError('Bad PDU type for reply %s at %s' % \
                                         (pdu.__class__.__name__,
                                          self.__class__.__name__))
        pdu.apiAlphaSetRequestId(self.apiAlphaGetRequestId().get())
        return pdu

    reply = apiAlphaReply

    def apiAlphaMatch(self, rspPdu):
        """Return true if response PDU matches this ours"""
        if not isinstance(rspPdu, rfc1157.GetResponsePdu):
            raise error.BadArgumentError('Non-response PDU to match %s vs %s'
                                         % (self.__class__.__name__, str(rspPdu)))
        return self.apiAlphaGetRequestId() == rspPdu.apiAlphaGetRequestId()

    match = apiAlphaMatch

# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass

class GetResponsePduMixIn(RequestPduMixIn):
    def apiAlphaGetErrorStatus(self): return self['error_status']
    def apiAlphaSetErrorStatus(self, value):
        self.apiAlphaSetSimpleComponent('error_status', value)
    def apiAlphaGetErrorIndex(self):
        errorIndex = self['error_index']
        if errorIndex > len(self.apiAlphaGetVarBindList()):
            raise error.BadArgumentError('Error index out of range (%s) at %s' % (errorIndex, self.__class__.__name__))
        return errorIndex
    def apiAlphaSetErrorIndex(self, value):
        self.apiAlphaSetSimpleComponent('error_index', value)
    
    def apiAlphaGetEndOfMibIndices(self):
        if self.apiAlphaGetErrorStatus() == 2:
            return [ self.apiAlphaGetErrorIndex().get() - 1 ]
        return []

    def apiAlphaSetEndOfMibIndices(self, *indices):
        for idx in indices:
            self.apiAlphaSetErrorStatus(2)
            self.apiAlphaSetErrorIndex(idx+1)
            break

# XXX A v2c-style alias
ResponsePduMixIn = GetResponsePduMixIn

class TrapPduMixIn(PduMixInBase):
    def apiAlphaGetEnterprise(self):
        return self['enterprise']
    def apiAlphaSetEnterprise(self, value):
        self.apiAlphaSetSimpleComponent('enterprise', value)
    def apiAlphaGetAgentAddr(self):
        return self['agent_addr']['internet']
    def apiAlphaSetAgentAddr(self, value):
        # XXX this might need to be moved to some inner method
        if type(value) == InstanceType:
            self['agent_addr']['internet'] = value
        else:
            self['agent_addr']['internet'].set(value)
    def apiAlphaGetGenericTrap(self):
        return self['generic_trap']
    def apiAlphaSetGenericTrap(self, value):
        self.apiAlphaSetSimpleComponent('generic_trap', value)
    def apiAlphaGetSpecificTrap(self):
        return self['specific_trap']
    def apiAlphaSetSpecificTrap(self, value):
        self.apiAlphaSetSimpleComponent('specific_trap', value)
    def apiAlphaGetTimeStamp(self):
        return self['time_stamp']
    def apiAlphaSetTimeStamp(self, value):
        self.apiAlphaSetSimpleComponent('time_stamp', value)

class MessageMixIn:
    def apiAlphaGetVersion(self): return self['version']
    def apiAlphaGetCommunity(self): return self['community']
    def apiAlphaSetCommunity(self, value):
        self.apiAlphaSetSimpleComponent('community', value)
    def apiAlphaGetPdu(self):
        if len(self['pdu']):
            return self['pdu'].values()[0]
        raise error.BadArgumentError('PDU not initialized at %s' % \
                                     self.__class__.__name__)
    
    def apiAlphaSetPdu(self, value): self['pdu'][None] = value
    def apiAlphaReply(self, rsp=None):
        """Return initialized response message
        """
        if rsp is None:
            rsp = rfc1157.Message()
            rsp.apiAlphaSetPdu(self.apiAlphaGetPdu().apiAlphaReply())
        else:
            self.apiAlphaGetPdu().apiAlphaReply(rsp.apiAlphaGetPdu())
        rsp.apiAlphaSetCommunity(self.apiAlphaGetCommunity().get())
        return rsp

    def apiAlphaMatch(self, rsp):
        """Return true if response message matches this request"""
        if not isinstance(rsp, rfc1157.Message):
            raise error.BadArgumentError('Non-message to match %s vs %s' %
                                         (self.__class__.__name__, str(rsp)))
        if self.apiAlphaGetCommunity() != rsp.apiAlphaGetCommunity():
            return
        return self.apiAlphaGetPdu().apiAlphaMatch(rsp.apiAlphaGetPdu())

    # Compatibility aliases
    reply = apiAlphaReply
    match = apiAlphaMatch
             
mixInComps = [ (rfc1157.VarBind, VarBindMixIn),
               (rfc1157.GetRequestPdu, GetRequestPduMixIn),
               (rfc1157.GetNextRequestPdu, GetNextRequestPduMixIn),
               (rfc1157.SetRequestPdu, SetRequestPduMixIn),
               (rfc1157.GetResponsePdu, GetResponsePduMixIn),
               (rfc1157.TrapPdu, TrapPduMixIn),
               (rfc1157.Message, MessageMixIn) ]

for (baseClass, mixIn) in mixInComps:
    if mixIn not in baseClass.__bases__:
        baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
