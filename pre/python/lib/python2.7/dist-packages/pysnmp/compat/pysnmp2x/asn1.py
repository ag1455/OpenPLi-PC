"""
   Deprecated PySNMP 2.0.x compatibility interface to SNMP subset of
   ASN.1 data types.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import pysnmp.proto.rfc1902, pysnmp.asn1.error, \
       pysnmp.asn1.encoding.ber.error, pysnmp.proto.error
from pysnmp.compat.pysnmp2x import error

class Error(error.Generic):
    """Base class for asn1 module exceptions
    """
    pass

class UnknownTag(Error):
    """Unknown BER tag
    """
    pass

class OverFlow(Error):
    """Data item does not fit the packet
    """
    pass

class UnderRun(Error):
    """Short BER data stream
    """
    pass

class BadEncoding(Error):
    """Incorrect BER encoding
    """
    pass

class TypeError(Error):
    """ASN.1 data type incompatibility
    """
    pass

class BadArgument(Error):
    """Malformed argument
    """
    pass

class CompatBase:
    """Base class for compatibility classes
    """
    def _wrapper_fun(self, fun, *args):
        """
        """
        try:
            return apply(fun, args)

        # Catch protocol package exceptions

        except pysnmp.proto.error.BadArgumentError, why:
            raise BadArgument(why)

        except pysnmp.proto.error.ProtoError, why:
            raise Error(why)

        # Catch ber package exceptions
        
        except pysnmp.asn1.encoding.ber.error.BadArgumentError, why:
            raise BadArgument(why)

        except pysnmp.asn1.encoding.ber.error.TypeMismatchError, why:
            raise UnknownTag(why)

        except pysnmp.asn1.encoding.ber.error.OverFlowError, why:
            raise OverFlow(why)

        except pysnmp.asn1.encoding.ber.error.UnderRunError, why:
            raise UnderRun(why)

        except pysnmp.asn1.encoding.ber.error.BadEncodingError, why:
            raise BadEncoding(why)

        except pysnmp.asn1.encoding.ber.error.BerEncodingError, why:
            raise Error(why)

        # Catch asn1 package exceptions
        
        except pysnmp.asn1.error.BadArgumentError, why:
            raise BadArgument(why)

        except pysnmp.asn1.error.ValueConstraintError, why:
            raise TypeError(why)

        except pysnmp.asn1.error.Asn1Error, why:
            raise Error(why)

    def decode(self, data):
        """Compatibility method: decode BER octet stream into this ASN.1 object
        """
        rest = self._wrapper_fun(self._decode_fun, data)
        return (self.get(), rest)

    def __init__(self, value=None):
        """Compatibility method: constructor
        """
        return self._wrapper_fun(self._init_fun, value)

    def encode(self, data=None):
        """Compatibility method: assign a value and encode it into BER octet stream
        """
        return self._wrapper_fun(self._encode_fun, data)

    def update(self, value):
        """Compatibility method: assign a value
        """
        return self._wrapper_fun(self._update_fun, value)

    def __call__(self):
        """Compatibility method: return a value
        """
        return self._wrapper_fun(self._call_fun)

    def __cmp__(self, other):
        """Compatibility method: comparation
        """
        return self._wrapper_fun(self._cmp_fun, other)
        
class INTEGER(CompatBase, pysnmp.proto.rfc1902.Integer):
    """Compatibility interface to ASN.1 Integer

    """
    _init_fun = pysnmp.proto.rfc1902.Integer.__init__
    _decode_fun = pysnmp.proto.rfc1902.Integer.decode
    _encode_fun = pysnmp.proto.rfc1902.Integer.encode
    _update_fun = pysnmp.proto.rfc1902.Integer.set
    _call_fun = pysnmp.proto.rfc1902.Integer.get
    _cmp_fun = pysnmp.proto.rfc1902.Integer.__cmp__

class UNSIGNED32(CompatBase, pysnmp.proto.rfc1902.Unsigned32):
    """Compatibility interface to ASN.1 Unsigned32
    """
    _init_fun = pysnmp.proto.rfc1902.Unsigned32.__init__
    _decode_fun = pysnmp.proto.rfc1902.Unsigned32.decode
    _encode_fun = pysnmp.proto.rfc1902.Unsigned32.encode
    _update_fun = pysnmp.proto.rfc1902.Unsigned32.set
    _call_fun = pysnmp.proto.rfc1902.Unsigned32.get
    _cmp_fun = pysnmp.proto.rfc1902.Unsigned32.__cmp__

class TIMETICKS(CompatBase, pysnmp.proto.rfc1902.TimeTicks):
    """Compatibility interface to ASN.1 TimeTicks
    """
    _init_fun = pysnmp.proto.rfc1902.TimeTicks.__init__
    _decode_fun = pysnmp.proto.rfc1902.TimeTicks.decode
    _encode_fun = pysnmp.proto.rfc1902.TimeTicks.encode
    _update_fun = pysnmp.proto.rfc1902.TimeTicks.set
    _call_fun = pysnmp.proto.rfc1902.TimeTicks.get
    _cmp_fun = pysnmp.proto.rfc1902.TimeTicks.__cmp__

class COUNTER32(CompatBase, pysnmp.proto.rfc1902.Counter32):
    """Compatibility interface to ASN.1 COUNTER32
    """
    _init_fun = pysnmp.proto.rfc1902.Counter32.__init__
    _decode_fun = pysnmp.proto.rfc1902.Counter32.decode
    _encode_fun = pysnmp.proto.rfc1902.Counter32.encode
    _update_fun = pysnmp.proto.rfc1902.Counter32.set
    _call_fun = pysnmp.proto.rfc1902.Counter32.get
    _cmp_fun = pysnmp.proto.rfc1902.Counter32.__cmp__

class COUNTER64(CompatBase, pysnmp.proto.rfc1902.Counter64):
    """Compatibility interface to ASN.1 COUNTER64
    """
    _init_fun = pysnmp.proto.rfc1902.Counter64.__init__
    _decode_fun = pysnmp.proto.rfc1902.Counter64.decode
    _encode_fun = pysnmp.proto.rfc1902.Counter64.encode
    _update_fun = pysnmp.proto.rfc1902.Counter64.set
    _call_fun = pysnmp.proto.rfc1902.Counter64.get
    _cmp_fun = pysnmp.proto.rfc1902.Counter64.__cmp__

class GAUGE32(CompatBase, pysnmp.proto.rfc1902.Gauge32):
    """Compatibility interface to ASN.1 GAUGE32
    """
    _init_fun = pysnmp.proto.rfc1902.Gauge32.__init__    
    _decode_fun = pysnmp.proto.rfc1902.Gauge32.decode
    _encode_fun = pysnmp.proto.rfc1902.Gauge32.encode
    _update_fun = pysnmp.proto.rfc1902.Gauge32.set
    _call_fun = pysnmp.proto.rfc1902.Gauge32.get
    _cmp_fun = pysnmp.proto.rfc1902.Gauge32.__cmp__

class OCTETSTRING(CompatBase, pysnmp.proto.rfc1902.OctetString):
    """Compatibility interface to ASN.1 OCTETSTRING
    """
    _init_fun = pysnmp.proto.rfc1902.OctetString.__init__    
    _decode_fun = pysnmp.proto.rfc1902.OctetString.decode
    _encode_fun = pysnmp.proto.rfc1902.OctetString.encode
    _update_fun = pysnmp.proto.rfc1902.OctetString.set
    _call_fun = pysnmp.proto.rfc1902.OctetString.get
    _cmp_fun = pysnmp.proto.rfc1902.OctetString.__cmp__

class OPAQUE(CompatBase, pysnmp.proto.rfc1902.Opaque):
    """Compatibility interface to ASN.1 OPAQUE
    """
    _init_fun = pysnmp.proto.rfc1902.Opaque.__init__
    _decode_fun = pysnmp.proto.rfc1902.Opaque.decode
    _encode_fun = pysnmp.proto.rfc1902.Opaque.encode
    _update_fun = pysnmp.proto.rfc1902.Opaque.set
    _call_fun = pysnmp.proto.rfc1902.Opaque.get
    _cmp_fun = pysnmp.proto.rfc1902.Opaque.__cmp__

class OBJECTID(CompatBase, pysnmp.proto.rfc1902.ObjectIdentifier):
    """Compatibility interface to ASN.1 OBJECTID
    """
    _init_fun = pysnmp.proto.rfc1902.ObjectIdentifier.__init__    
    _decode_fun = pysnmp.proto.rfc1902.ObjectIdentifier.decode
    _encode_fun = pysnmp.proto.rfc1902.ObjectIdentifier.encode
    _update_fun = pysnmp.proto.rfc1902.ObjectIdentifier.set
    _call_fun = pysnmp.proto.rfc1902.ObjectIdentifier.get
    _cmp_fun = pysnmp.proto.rfc1902.ObjectIdentifier.__cmp__
    _isaprefix_fun = pysnmp.proto.rfc1902.ObjectIdentifier.isaprefix
    _str2num_fun = pysnmp.proto.rfc1902.ObjectIdentifier.str2num
    _num2str_fun = pysnmp.proto.rfc1902.ObjectIdentifier.num2str
    
    def isaprefix(self, other):
        """Compatibility method: returns true if the payload of class instance
           is a prefix of the other
        """
        return self._wrapper_fun(self._isaprefix_fun, other)

    def str2num(self, other, aliases=None):
        """Compatibility method: converts an Object ID oid into a list of
           integer sub-Object-IDs
        """
        return self._wrapper_fun(self._str2num_fun, other)

    def num2str(self, other, aliases=None):
        """Compatibility method: converts an Object ID oid into dotted notation

        """
        return self._wrapper_fun(self._num2str_fun, other)

class IPADDRESS(CompatBase, pysnmp.proto.rfc1902.IpAddress):
    """Compatibility interface to ASN.1 IPADDRESS
    """
    _init_fun = pysnmp.proto.rfc1902.IpAddress.__init__
    _decode_fun = pysnmp.proto.rfc1902.IpAddress.decode
    _encode_fun = pysnmp.proto.rfc1902.IpAddress.encode
    _update_fun = pysnmp.proto.rfc1902.IpAddress.set
    _call_fun = pysnmp.proto.rfc1902.IpAddress.get
    _cmp_fun = pysnmp.proto.rfc1902.IpAddress.__cmp__

class NULL(CompatBase, pysnmp.proto.rfc1902.Null):
    """Compatibility interface to ASN.1 NULL
    """
    _init_fun = pysnmp.proto.rfc1902.Null.__init__
    _decode_fun = pysnmp.proto.rfc1902.Null.decode
    _encode_fun = pysnmp.proto.rfc1902.Null.encode
    _update_fun = pysnmp.proto.rfc1902.Null.set
    _call_fun = pysnmp.proto.rfc1902.Null.get
    _cmp_fun = pysnmp.proto.rfc1902.Null.__cmp__

def decode(data):
    """
       decode(input) -> (<asn1-object>, rest)

       Decode input octet stream (string) into ASN.1 object and return
       the rest of input (string).
    """
    for objType in [ INTEGER, UNSIGNED32, TIMETICKS, COUNTER32, COUNTER64,
                     GAUGE32, OCTETSTRING, OPAQUE, OBJECTID, IPADDRESS,
                     NULL ]:
        obj = objType()
        try:
            rest = obj.decode(data)

        except UnknownTag:
            continue
        
        return (obj, rest)

    raise UnknownTag('Unsuppored ASN.1 data type')
