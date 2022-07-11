from pysnmp.proto.rfc1902 import *
from pysnmp.proto.rfc1905 import *
from pysnmp.proto.api.alpha import rfc1905, pdutypes

# Proto versions compatibility alias
GetResponsePdu = ResponsePdu
TrapPdu = SnmpV2TrapPdu

pduTypes = { pdutypes.GetRequestPduType(): GetRequestPdu,
             pdutypes.GetNextRequestPduType(): GetNextRequestPdu,
             pdutypes.SetRequestPduType(): SetRequestPdu,
             pdutypes.GetResponsePduType(): ResponsePdu,
             pdutypes.TrapPduType(): SnmpV2TrapPdu,
             pdutypes.GetBulkRequestPduType(): GetBulkRequestPdu,             
             pdutypes.InformRequestPduType(): InformRequestPdu,
             pdutypes.ReportPduType(): ReportPdu }
