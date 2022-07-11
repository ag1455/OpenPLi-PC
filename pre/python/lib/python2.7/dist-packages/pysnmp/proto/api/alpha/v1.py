from pysnmp.proto.rfc1155 import *
from pysnmp.proto.rfc1157 import *
from pysnmp.proto.api.alpha import rfc1155, rfc1157, pdutypes

pduTypes = { pdutypes.GetRequestPduType(): GetRequestPdu,
             pdutypes.GetNextRequestPduType(): GetNextRequestPdu,
             pdutypes.SetRequestPduType(): SetRequestPdu,
             pdutypes.GetResponsePduType(): GetResponsePdu,
             pdutypes.TrapPduType(): TrapPdu }

