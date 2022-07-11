"""
   Compatibility API to SMI and SNMP for v.1 (RFC1155 & RFC1157). Do
   not use it in new projects.

   Copyright 1999-2004 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'GetRequest', 'GetNextRequest', 'SetRequest', 'Trap', \
            'GetResponse', 'Request' ]

from pysnmp.proto.rfc1155 import *
from pysnmp.proto import rfc1157, error
from pysnmp.asn1.encoding.ber.error import TypeMismatchError

# These do not require any additional subtyping
from pysnmp.proto.rfc1157 import VarBind, VarBindList

class MessageBase(rfc1157.Message):
    def __init__(self, **kwargs):
        # Compatibility stub: initialize PDU type
        apply(rfc1157.Message.__init__, [self], kwargs)
        self['pdu'][None] = self.compatMessagePdu()

    def decode(self, wholeMsg):
        rest = rfc1157.Message.decode(self, wholeMsg)
        if not isinstance(self['pdu'].values()[0], self.compatMessagePdu):
            raise TypeMismatchError('Mismatch PDU type')
        return rest
        
class GetRequest(MessageBase): compatMessagePdu = rfc1157.GetRequestPdu
class GetNextRequest(MessageBase): compatMessagePdu = rfc1157.GetNextRequestPdu
class SetRequest(MessageBase): compatMessagePdu = rfc1157.SetRequestPdu
class Trap(MessageBase): compatMessagePdu = rfc1157.TrapPdu
class GetResponse(MessageBase): compatMessagePdu = rfc1157.GetResponsePdu

# An alias to make it looking similar to v.2c
Response = GetResponse

# Requests demux
class Request(rfc1157.Message): pass
