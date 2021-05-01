"""
   An implementation of high-level API to SNMP v.2c message PDU objects
   (RFC1905)

   Copyright 1999-2004 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.proto import rfc1905
from pysnmp.proto.api.alpha import rfc1157
from pysnmp.proto.api import error

class VarBindMixIn(rfc1157.VarBindMixIn): pass

class PduMixInBase(rfc1157.PduMixInBase):
    def apiAlphaSetVarBindList(self, *varBinds):
        varBindList = self['variable_bindings']
        idx = 0
        for varBind in varBinds:
            if isinstance(varBind, rfc1905.VarBind):
                varBindList[idx] = varBind
            else:
                if len(varBindList) <= idx:
                    varBindList.append(varBindList.componentFactoryBorrow())
                varBindList[idx].apiAlphaSetOidVal(varBind)
            idx = idx + 1
        del varBindList[idx:]

class RequestPduMixIn(PduMixInBase, rfc1157.RequestPduMixIn):
    def apiAlphaReply(self, pdu=None):
        """Return initialized response PDU
        """
        if pdu is None:
            pdu = rfc1905.ResponsePdu()
        elif not isinstance(pdu, rfc1905.ResponsePdu):
            raise error.BadArgumentError('Bad PDU type for reply %s at %s' % \
                                         (pdu.__class__.__name__,
                                          self.__class__.__name__))
        pdu.apiAlphaSetRequestId(self.apiAlphaGetRequestId())
        return pdu

    reply = apiAlphaReply

    def apiAlphaMatch(self, rspPdu):
        """Return true if response PDU matches this ours"""
        if not isinstance(rspPdu, rfc1905.ResponsePdu):
            raise error.BadArgumentError('Non-response PDU to match %s vs %s'
                                         % (self.__class__.__name__, str(rspPdu)))
        return self.apiAlphaGetRequestId() == rspPdu.apiAlphaGetRequestId()

    match = apiAlphaMatch

# Request PDU mix-ins
class GetRequestPduMixIn(RequestPduMixIn): pass
class GetNextRequestPduMixIn(RequestPduMixIn): pass
class SetRequestPduMixIn(RequestPduMixIn): pass
class InformRequestPduMixIn(RequestPduMixIn): pass
class ReportPduMixIn(PduMixInBase): pass
class SnmpV2TrapPduMixIn(PduMixInBase): pass

class ResponsePduMixIn(RequestPduMixIn, rfc1157.GetResponsePduMixIn):
    def apiAlphaGetEndOfMibIndices(self):
        indices = []; idx = 0
        for varBind in self.apiAlphaGetVarBindList():
            oid, val = varBind.apiAlphaGetOidVal()
            if isinstance(val, rfc1905.EndOfMibView):
                indices.append(idx)
            idx = idx + 1
        indices.reverse()
        return indices

    def apiAlphaSetEndOfMibIndices(self, *indices):
        varBinds = self.apiAlphaGetVarBindList()
        for idx in indices:
            bindValue = varBinds[idx-1]['value']
            bindValue['endOfMibView'] = bindValue.componentFactoryBorrow('endOfMibView')

# A v1-style alias
GetResponsePduMixIn = ResponsePduMixIn
    
class GetBulkRequestPduMixIn(RequestPduMixIn):
    def apiAlphaGetNonRepeaters(self): return self['non_repeaters']
    def apiAlphaSetNonRepeaters(self, value): self['non_repeaters'].set(value)
    def apiAlphaGetMaxRepetitions(self): return self['max_repetitions']
    def apiAlphaSetMaxRepetitions(self, value):
        self['max_repetitions'].set(value)

    def apiAlphaGetTableIndices(self, rsp, *headerVars):
        nonRepeaters = self.apiAlphaGetNonRepeaters().get()
        N = min(nonRepeaters, len(self.apiAlphaGetVarBindList()))
        R = max(len(self.apiAlphaGetVarBindList())-N, 0)
        if R == 0:
            M = 0
        else:
            M = min(self.apiAlphaGetMaxRepetitions().get(), \
                    (len(rsp.apiAlphaGetVarBindList())-N)/R)
        if len(headerVars) < R + N:
            raise error.BadArgumentError('Short table header')                
        endOfMibIndices = rsp.apiAlphaGetEndOfMibIndices()
        varBindList = rsp.apiAlphaGetVarBindList()        
        varBindRows = []; varBindTable = [ varBindRows ]
        for idx in range(N):
            if idx in endOfMibIndices:
                varBindRows.append(-1)
                continue
            oid, val = varBindList[idx].apiAlphaGetOidVal()
            # XXX isaprefix rename
            if not headerVars[idx].isaprefix(oid):
                varBindRows.append(-1)
                continue
            varBindRows.append(idx)
        for rowIdx in range(M):
            if len(varBindTable) < rowIdx+1:
                varBindTable.append([])
            varBindRow = varBindTable[-1]
            for colIdx in range(R):
                while rowIdx and len(varBindRow) < N:
                    varBindRow.append(varBindTable[-2][colIdx])
                if len(varBindRow) < colIdx+N+1:
                    varBindRow.append(-1)
                idx = N + rowIdx*R + colIdx
                oid, val = varBindList[idx].apiAlphaGetOidVal()
                if headerVars[colIdx+N].isaprefix(oid):
                    varBindRow[-1] = idx
        return varBindTable

class MessageMixIn(rfc1157.MessageMixIn):
    def apiAlphaReply(self, rsp=None):
        """Return initialized response message
        """
        if rsp is None:
            rsp = rfc1905.Message()
            rsp.apiAlphaSetPdu(self.apiAlphaGetPdu().apiAlphaReply())
        else:
            self.apiAlphaGetPdu().apiAlphaReply(rsp.apiAlphaGetPdu())
        rsp.apiAlphaSetCommunity(self.apiAlphaGetCommunity())
        return rsp

    def apiAlphaMatch(self, rsp):
        """Return true if response message matches this request"""
        if not isinstance(rsp, rfc1905.Message):
            raise error.BadArgumentError('Non-message to match %s vs %s' %
                                         (self.__class__.__name__, str(rsp)))
        if self.apiAlphaGetCommunity() != rsp.apiAlphaGetCommunity():
            return
        return self.apiAlphaGetPdu().apiAlphaMatch(rsp.apiAlphaGetPdu())

    # Compatibility aliases
    reply = apiAlphaReply
    match = apiAlphaMatch

mixInComps = [ (rfc1905.VarBind, VarBindMixIn),
               (rfc1905.GetRequestPdu, GetRequestPduMixIn),
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
