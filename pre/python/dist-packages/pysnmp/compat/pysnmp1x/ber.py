"""
   Deprecated PySNMP 1.x compatibility interface to ASN.1 data types handlers.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.proto import rfc1155
from pysnmp.compat.pysnmp1x import wrapexp, error

class ber(wrapexp.Base):
    """Depricated PySNMP 1.x compatibility ASN.1 types processing class
    """

    # Integer
    
    def _encode_integer_fun(self, integer):
        """Compatibility method: encode integer
        """
        return rfc1155.Integer(integer).encode()

    def encode_integer(self, integer):
        """
           encode_integer(integer) -> octet stream
        
           Encode ASN.1 integer into octet stream.
        """
        return self._wrapper(self._encode_integer_fun, integer)

    def _decode_integer_fun(self, octetStream):
        """Compatibility method: decode integer
        """
        obj = rfc1155.Integer(); obj.decode(octetStream)
        return obj.get()

    def decode_integer(self, octetStream):
        """
           decode_integer(stream) -> integer

           Decode octet stream into signed ASN.1 integer.
        """
        return self._wrapper(self._decode_integer_fun, octetStream)

    # String

    def _encode_string_fun(self, string):
        """Compatibility method: encode string
        """
        return rfc1155.OctetString(string).encode()

    def encode_string(self, string):
        """
           encode_string(string) -> octet stream
        
           Encode ASN.1 string into octet stream.
        """
        return self._wrapper(self._encode_string_fun, string)
    
    def _decode_string_fun(self, octetStream):
        """Compatibility method: decode string
        """
        obj = rfc1155.OctetString(); obj.decode(octetStream)
        return obj.get()

    def decode_string(self, octetStream):
        """
           decode_string(stream) -> string

           Decode octet stream into signed ASN.1 string.
        """
        return self._wrapper(self._decode_string_fun, octetStream)

    # OID

    def _encode_oid_fun(self, noids):
        """Compatibility method: encode objectID
        """
        oid = rfc1155.ObjectIdentifier()
        return oid.encode(oid.num2str(noids))

    def encode_oid(self, noids):
        """
           encode_oid(oids) -> octet stream

           Encode ASN.1 Object ID (specified as a list of integer subIDs)
           into octet stream.
        """
        return self._wrapper(self._encode_oid_fun, noids)
    
    def _decode_oid_fun(self, octetStream):
        """Compatibility method: decode objectID
        """
        obj = rfc1155.ObjectIdentifier(); obj.decode(octetStream)
        return obj.str2num(obj.get())

    def decode_oid(self, octetStream):
        """
           decode_oid(stream) -> object id

           Decode octet stream into ASN.1 Object ID (returned as a list of
           integer subIDs).
        """
        return self._wrapper(self._decode_oid_fun, octetStream)

    def _oid_prefix_check_fun(self, enc_oid_1, enc_oid_2):
        """Compatibility method: compare OIDs
        """
        obj1 = rfc1155.ObjectIdentifier(); obj1.decode(enc_oid_1)
        obj2 = rfc1155.ObjectIdentifier(); obj2.decode(enc_oid_2)
        return obj1.isaprefix(obj2)
    
    def oid_prefix_check(self, enc_oid_1, enc_oid_2):
        """
           oid_prefix_check(encoded_oid_1, encoded_oid_2) -> boolean

           Compare encoded OIDs (given as lists), return non-None if
           OID1 is a prefix of OID2.

           This is intended to be used for MIB tables retrieval.
        """
        return self._wrapper(self._oid_prefix_check_fun, enc_oid_1, enc_oid_2)

    def _str2nums_fun(self, txt):
        """Compatibility method: convert OID
        """
        return rfc1155.ObjectIdentifier().str2num(txt)

    def str2nums(self, txt, aliases=None):
        """
           str2nums(obj_id) -> object id

           Convert Object ID (given as string) into a list of integer
           sub IDs.
        """
        return self._wrapper(self._str2nums_fun, txt)

    def _nums2str_fun(self, objid_n):
        """Compatibility method: convert OID
        """
        return rfc1155.ObjectIdentifier().nums2str(objid_n)

    def nums2str(self, objid_n, aliases=None):
        """
           nums2str(obj_id) -> object id

           Convert Object ID (given as a list of integer sub Object IDs) into
           string representation.
        """
        return self._wrapper(self._nums2str_fun, objid_n)

    # IP address

    def _encode_ipaddr_fun(self, addr):
        """Compatibility method: encode IP address
        """
        obj = rfc1155.IpAddress(addr)
        return obj.encode()

    def encode_ipaddr(self, addr):
        """
           encode_addr(addr) -> octet stream

           Encode ASN.1 IP address (in dotted notation) into octet stream.
        """
        return self._wrapper(self._encode_ipaddr_fun, addr)
    
    def _decode_ipaddr_fun(self, octetStream):
        """Compatibility method: decode IP address
        """
        obj = rfc1155.IpAddress(); obj.decode(octetStream)
        return obj.get()

    def decode_ipaddr(self, octetStream):
        """
           decode_ipaddr(stream) -> IP address

           Decode octet stream into ASN.1 IP address (in dotted notation)
        """
        return self._wrapper(self._decode_ipaddr_fun, octetStream)

    # Timeticks

    def _encode_timeticks_fun(self, timeticks):
        """Compatibility method: encode timeticks
        """
        obj = rfc1155.TimeTicks(timeticks)
        return obj.encode()

    def encode_timeticks(self, timeticks):
        """
           encode_timeticks(timeticks) -> octet stream

           Encode ASN.1 timeticks into octet stream.
        """
        return self._wrapper(self._encode_timeticks_fun, timeticks)
    
    def _decode_timeticks_fun(self, octetStream):
        """Compatibility method: decode timeticks
        """
        obj = rfc1155.TimeTicks(); obj.decode(octetStream)
        return obj.get()

    def decode_timeticks(self, octetStream):
        """
           decode_timeticks(stream) -> timeticks

           Decode octet stream into ASN.1 timeticks
        """
        return self._wrapper(self._decode_timeticks_fun, octetStream)

    # Compatibility alias
    decode_uptime = decode_timeticks
    
    # Null

    def _encode_null_fun(self):
        """Compatibility method: encode null
        """
        obj = rfc1155.Null()
        return obj.encode()

    def encode_null(self):
        """
           encode_null() -> octet stream

           Encode ASN.1 Null into octet stream.
        """
        return self._wrapper(self._encode_null_fun)
    
    def _decode_null_fun(self, octetStream):
        """Compatibility method: decode Null
        """
        obj = rfc1155.Null(); obj.decode(octetStream)
        return obj.get()

    def decode_null(self, octetStream):
        """
           decode_null(stream) -> Null

           Decode octet stream into ASN.1 Null
        """
        return self._wrapper(self._decode_null_fun, octetStream)

    # Universal decoder

    def _decode_value_fun(self, octetStream):
        """Compatibility method: decode any of supported ASN.1 value
        """
        obj = rfc1155.ObjectSyntax(); obj.decode(octetStream)
        if obj.has_key('address'):
            return obj.values()[0].values()[0].values()[0].get()
        else:
            return obj.values()[0].values()[0].get()
        
    def decode_value(self, octetStream):
        """
           decode_value(stream) -> value

           Decode octet stream into ASN.1 value (its ASN.1 type is
           determined from included BER tag). The type of returned
           value is context dependent.
        """
        return self._wrapper(self._decode_value_fun, octetStream)
