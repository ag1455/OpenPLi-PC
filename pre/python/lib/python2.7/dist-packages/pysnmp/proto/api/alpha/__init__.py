"""A high-level API to SNMP protocol objects.
"""
from pysnmp.proto.api.alpha import pdutypes, versions
from pysnmp.proto.api.alpha import v1, v2c

# Protocol versions
protoVersionId1 = versions.ProtoVersionId1()
protoVersionId2c = versions.ProtoVersionId2c()
protoVersions = { protoVersionId1: v1, protoVersionId2c: v2c }

class MetaMessage(v1.Choice):
    """A selection of SNMP protocol Messages"""
    choiceNames = [ protoVersionId1, protoVersionId2c ]
    choiceComponents = [ v1.Message, v2c.Message ]

# PDU types
getRequestPduType = pdutypes.GetRequestPduType()
getNextRequestPduType = pdutypes.GetNextRequestPduType()
setRequestPduType = pdutypes.SetRequestPduType()
getResponsePduType = responsePduType = pdutypes.GetResponsePduType()
trapPduType = pdutypes.TrapPduType()
getBulkRequestPduType = pdutypes.GetBulkRequestPduType()
informRequestPduType = pdutypes.InformRequestPduType()
reportPduType = pdutypes.ReportPduType()
