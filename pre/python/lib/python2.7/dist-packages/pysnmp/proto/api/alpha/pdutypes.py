"""SNMP version independent PDU type classes"""
from pysnmp.proto import rfc1157, rfc1905

class PduTypeMixInBase:
    def apiAlphaGetPduType(self):
        return self.apiAlphaPduType

# MixIn's

# Common v1/v2c types
class GetRequestPduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'GetRequest'
class GetNextRequestPduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'GetNextRequest'
class SetRequestPduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'SetRequest'
class GetResponsePduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'GetResponse'
class TrapPduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'Trap'

# v2c only types
class GetBulkRequestPduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'BulkRequest'
class InformRequestPduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'InformRequest'
class ReportPduTypeMixIn(PduTypeMixInBase):
    apiAlphaPduType = 'Report'

# Stand-alone PDU types
class PduTypeBase:
    def __hash__(self): return hash(self.apiAlphaPduType)
    def __cmp__(self, other): return cmp(self.apiAlphaPduType, other)
    def __str__(self): return str(self.apiAlphaPduType)

# Common v1/v2c types
class GetRequestPduType(PduTypeBase, GetRequestPduTypeMixIn): pass
class GetNextRequestPduType(PduTypeBase, GetNextRequestPduTypeMixIn): pass
class SetRequestPduType(PduTypeBase, SetRequestPduTypeMixIn): pass
class GetResponsePduType(PduTypeBase, GetResponsePduTypeMixIn): pass
class TrapPduType(PduTypeBase, TrapPduTypeMixIn): pass

# v2c only types
class GetBulkRequestPduType(PduTypeBase, GetBulkRequestPduTypeMixIn): pass
class InformRequestPduType(PduTypeBase, InformRequestPduTypeMixIn): pass
class ReportPduType(PduTypeBase, ReportPduTypeMixIn): pass

mixInComps = [ (rfc1157.GetRequestPdu, GetRequestPduTypeMixIn),
               (rfc1157.GetNextRequestPdu, GetNextRequestPduTypeMixIn),
               (rfc1157.SetRequestPdu, SetRequestPduTypeMixIn),
               (rfc1157.GetResponsePdu, GetResponsePduTypeMixIn),
               (rfc1157.TrapPdu, TrapPduTypeMixIn),
               (rfc1905.GetRequestPdu, GetRequestPduTypeMixIn),
               (rfc1905.GetNextRequestPdu, GetNextRequestPduTypeMixIn),
               (rfc1905.SetRequestPdu, SetRequestPduTypeMixIn),
               (rfc1905.ResponsePdu, GetResponsePduTypeMixIn),
               (rfc1905.GetBulkRequestPdu, GetBulkRequestPduTypeMixIn),
               (rfc1905.InformRequestPdu, InformRequestPduTypeMixIn),
               (rfc1905.ReportPdu, ReportPduTypeMixIn),
               (rfc1905.TrapPdu, TrapPduTypeMixIn) ]

for (baseClass, mixIn) in mixInComps:
    if mixIn not in baseClass.__bases__:
        baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
