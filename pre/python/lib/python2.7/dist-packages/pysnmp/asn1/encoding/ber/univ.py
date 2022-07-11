"""
   Basic Encoding Rules implementation for "universal" ASN.1 data types.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.

   The BER processing part of this code has been partially derived
   from Simon Leinen's <simon@switch.ch> BER Perl module.
"""
# Module public names
__all__ = [ 'BooleanMixIn', 'IntegerMixIn', 'BitStringMixIn', \
            'OctetStringMixIn', 'NullMixIn', 'ObjectIdentifierMixIn', \
            'RealMixIn', 'EnumeratedMixIn', 'SequenceMixIn', \
            'SequenceOfMixIn', 'SetMixIn', 'SetOfMixIn', 'ChoiceMixIn' ]

from string import join
from pysnmp.asn1 import univ, oid
from pysnmp.asn1.encoding.ber import base, error

class BooleanMixIn(base.SimpleAsn1Object):
    """Implements BER processing for an ASN.1 boolean object
    """
    def _berEncode(self, value):
        """Encode boolean value
        """
        if value:
            return '\377'
        else:
            return '\000'

    def _berDecode(self, input):
        """Decode input into boolean value
        """
        if len(input) != 1:
            raise error.BadEncodingError('Input of wrong size (%d) for %s' %\
                                         (len(input), self.__class__.__name__))
        if ord(input[0]):
            return 1
        else:
            return 0

class IntegerMixIn(base.SimpleAsn1Object):
    """Implements BER processing for an ASN.1 integer object
    """
    def _berEncode(self, integer):
        """
           _berEncode() -> octet stream
           
           Encode tagged integer into octet stream.
        """
        result = ''
        
        # The 0 and -1 values need to be handled separately since
        # they are the terminating cases of the positive and negative
        # cases repectively.
        if integer == 0:
            result = '\000'
            
        elif integer == -1:
            result = '\377'
            
        elif integer < 0:
            while integer <> -1:
                (integer, result) = integer>>8, chr(integer & 0xff) + result
                
            if ord(result[0]) & 0x80 == 0:
                result = chr(0xff) + result
        else:
            while integer > 0:
                (integer, result) = integer>>8, chr(integer & 0xff) + result
                
            if (ord(result[0]) & 0x80 <> 0):
                result = chr(0x00) + result

        return result

    def _berDecode(self, input):
        """
           _berDecode(input) -> IntValue
           
           Decode octet stream into signed ASN.1 integer (of any length).
        """
        bytes = map(ord, input)
        if not len(bytes):
            raise error.BadEncodingError('Empty value at %s' % \
                                         self.__class__.__name__)
        if bytes[0] & 0x80:
            bytes.insert(0, -1L)

        result = reduce(lambda x,y: x<<8 | y, bytes, 0L)

        try:
            return int(result)

        except OverflowError:
            return result

class OctetStringMixIn(base.SimpleAsn1Object):
    """Implements BER processing for an ASN.1 OCTETSTRING object
    """
    def _berEncode(self, value):
        """Encode octet string value
        """
        return value

    def _berDecode(self, input):
        """Decode input into octet string value
        """
        return input

class BitStringMixIn(OctetStringMixIn):
    """BER for ASN.1 BITSTRING type
    """
    pass

class NullMixIn(base.SimpleAsn1Object):
    """BER for ASN.1 NULL object
    """
    def _berEncode(self, value):
        """Encode ASN.1 NULL value
        """
        return ''

    def _berDecode(self, input):
        """Decode input into ASN.1 NULL value
        """
        if len(input) != 0:
            raise error.BadEncodingError('Input of wrong size (%d) for %s' %\
                                         (len(input), self.__class__.__name__))
        return ''

class ObjectIdentifierMixIn(base.SimpleAsn1Object):
    """BER for ASN.1 OBJECTIDENTIFIER object
    """
    BER_FORWARD_CACHE = {}
    BER_BACKWARD_CACHE = {}
    def berInternEncoding( cls, oid ):
        """Given an OID value, cache the BER encoded values for reference"""
        from pysnmp.asn1.oid import OID
        encoded = cls._berEncode( OID(oid) )
        cls.BER_FORWARD_CACHE[ oid ] = encoded
        cls.BER_BACKWARD_CACHE[ encoded ] = oid
        # eventually likely to cache the other way as well
        return encoded
    berInternEncoding = classmethod( berInternEncoding )
    def _berEncode(cls, oid):
        """
           _berEncode() -> octet stream
           
           Encode ASN.1 Object ID into octet stream.
        """
        try:
            if cls.BER_FORWARD_CACHE.has_key( oid ):
                return cls.BER_FORWARD_CACHE[ oid ]
        except TypeError, err:
            pass
        # Make sure the Object ID is long enough
        if len(oid) < 2:
            raise error.BadArgumentError('Short Object ID for %s' % \
                                         cls.__name__)

        # Build the first twos
        index = 0
        result = oid[index] * 40
        result = result + oid[index+1]
        try:
            result = [ '%c' % int(result) ]

        except OverflowError:
            raise error.BadArgumentError('Initial sub-ID overflow %s for %s'%\
                                         (str(oid[index:]), \
                                          cls.__name__))

        # Setup index
        index = index + 2

        # Cycle through subids
        for subid in oid[index:]:
            if subid > -1 and subid < 128:
                # Optimize for the common case
                result.append('%c' % (subid & 0x7f))

            elif subid < 0 or subid > 0xFFFFFFFFL:
                raise error.BadArgumentError('SubId overflow %s for %s' %\
                                             (str(subid), \
                                              cls.__name__))

            else:
                # Pack large Sub-Object IDs
                res = [ '%c' % (subid & 0x7f) ]
                subid = subid >> 7
                while subid > 0:
                    res.insert(0, '%c' % (0x80 | (subid & 0x7f)))
                    subid = subid >> 7

                # Convert packed Sub-Object ID to string and add packed
                # it to resulted Object ID
                result.append(join(res, ''))

        # Convert BER encoded Object ID to string and return
        return join(result, '')
    _berEncode = classmethod( _berEncode )
        
    def _berDecode(cls, input):
        """
           _berDecode(input)
           
           Decode octet stream into ASN.1 Object ID
        """
        if cls.BER_BACKWARD_CACHE.has_key( input ):
            return cls.BER_BACKWARD_CACHE[ input ]
        oid = []
        index = 0

        if len(input) == 0:
            raise error.BadArgumentError('Short Object ID at %s'
                                         % cls.__name__)
        # Get the first subid
        subid = ord(input[index])
        oid.append(int(subid / 40))
        oid.append(int(subid % 40))

        index = index + 1

        # Loop through the rest
        while index < len(input):
            # Get a subid
            subid = ord(input[index])

            if subid < 128:
                oid.append(subid)
                index = index + 1
            else:
                # Construct subid from a number of octets
                next = subid
                subid = 0
                while next >= 128:
                    # Collect subid
                    subid = (subid << 7) + (next & 0x7F)

                    # Take next octet
                    index = index + 1
                    next = ord(input[index])

                    # Just for sure
                    if index > len(input):
                        raise error.BadArgumentError('Malformed sub-Object ID at %s'
                                                     % cls.__name__)

                # Append a subid to oid list
                subid = (subid << 7) + next
                oid.append(subid)
                index = index + 1

        return oid
    _berDecode = classmethod( _berDecode )

class RealMixIn(base.SimpleAsn1Object):
    """BER for ASN.1 REAL object
    """
    pass

class EnumeratedMixIn(IntegerMixIn):
    """Same as Integer
    """
    pass

# BER for structured ASN.1 objects

class SequenceMixIn(base.OrderedFixedTypeAsn1Object):
    """Implements BER processing for an ASN.1 SEQUENCE object
    """
    pass

class SequenceOfMixIn(base.OrderedVariableTypeAsn1Object):
    """Implements BER processing for an ASN.1 SEQUENCE OF object
    """
    pass

class SetMixIn(base.UnorderedFixedTypeAsn1Object):
    """Implements BER processing for an ASN.1 SET object
    """
    pass

class SetOfMixIn(base.UnorderedVariableTypeAsn1Object):
    """Implements BER processing for an ASN.1 SET OF object
    """
    pass

class ChoiceMixIn(base.SingleFixedTypeAsn1Object):
    """Implements BER processing for an ASN.1 CHOICE object
    """
    pass

mixInComps = [ (univ.Boolean, BooleanMixIn),
               (univ.Integer, IntegerMixIn),
               (univ.BitString, BitStringMixIn),
               (univ.OctetString, OctetStringMixIn),
               (univ.Null, NullMixIn),
               (univ.ObjectIdentifier, ObjectIdentifierMixIn),
               (univ.Real, RealMixIn),
               (univ.Enumerated, EnumeratedMixIn),
               (univ.Sequence, SequenceMixIn),
               (univ.SequenceOf, SequenceOfMixIn),
               (univ.Set, SetMixIn),
               (univ.SetOf, SetOfMixIn),
               (univ.Choice, ChoiceMixIn) ]
    
for (baseClass, mixIn) in mixInComps:
    if mixIn not in baseClass.__bases__:
        baseClass.__bases__ = baseClass.__bases__ + (mixIn, )
