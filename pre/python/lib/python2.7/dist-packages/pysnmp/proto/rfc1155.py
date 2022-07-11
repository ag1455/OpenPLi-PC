"""
   Implementation of data types defined by SNMP SMI (RFC1155, RFC1212)

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'Integer', 'OctetString', 'Null', 'ObjectIdentifier', \
            'IpAddress', 'Counter', 'Gauge', 'TimeTicks', 'Opaque', \
            'Sequence', 'SequenceOf', 'Choice', 'NetworkAddress', \
            'ObjectName', 'SimpleSyntax', 'ApplicationSyntax', \
            'ObjectSyntax']

from string import split, atoi, atoi_error
from types import StringType
from pysnmp.asn1.base import tagClasses
from pysnmp.asn1 import univ, constraints
import pysnmp.asn1.encoding.ber
from pysnmp.proto import error

# SimpleSyntax

class Integer(univ.Integer):
    """SMI INTEGER data type
    """
    pass

class OctetString(univ.OctetString):
    """SMI OCTETSTRING data type
    """
    pass

class Null(univ.Null):
    """SMI NULL data type
    """
    pass

class ObjectIdentifier(univ.ObjectIdentifier):
    """SMI OBJECTIDENTIFIER data type
    """
    pass

# ApplicationSyntax

class IpAddress(univ.OctetString):
    """SNMP IP address object (taken and returned as string in conventional
       "dotted" representation)
    """
    # Implicit tagging
    tagClass = tagClasses['APPLICATION']
    tagId = 0x00

    # Subtyping -- size constraint
    constraints = (
        constraints.ValueSizeConstraint( 4,4 ),
    )

    # Just for clarity
    initialValue = '0.0.0.0'
    
    def _iconv(self, value):
        """Convert IP address given in dotted notation into an unsigned
           int value
        """
        try:
            packed = split(value, '.')

        except:
            raise error.BadArgumentError('Malformed IP address %s for %s' % (str(value), self.__class__.__name__))
        
        # Make sure it is four octets length
        if len(packed) != 4:
            raise error.BadArgumentError('Malformed IP address %s for %s' % (str(value), self.__class__.__name__))

        # Convert string octets into integer counterparts
        try:
            return reduce(lambda x, y: x+y, \
                          map(lambda x: chr(atoi(x)), packed))

        except atoi_error:
            raise error.BadArgumentError('Malformed IP address %s for %s' % (str(value), self.__class__.__name__))

    def _oconv(self, value):
        """Convert unsigned int value into IP address dotted representation
        """
        return '%d.%d.%d.%d' % (ord(value[0]), ord(value[1]), \
                                ord(value[2]), ord(value[3]))

class Counter(univ.Integer):
    """SNMP Counter object
    """
    # Implicit tagging
    tagClass = tagClasses['APPLICATION']
    tagId = 0x01

    # Subtyping -- value range constraint
    constraints = (
        constraints.ValueRangeConstraint(0, 4294967295L),
    )



class Gauge(univ.Integer):
    """SNMP Gauge object
    """
    # Implicit tagging
    tagClass = tagClasses['APPLICATION']
    tagId = 0x02

    # Subtyping -- value range constraint
    constraints = (
        constraints.ValueRangeConstraint(0, 4294967295L),
    )

class TimeTicks(univ.Integer):
    """SNMP TIMETICKS object
    """
    # Implicit tagging
    tagClass = tagClasses['APPLICATION']
    tagId = 0x03

    # Subtyping -- value range constraint
    constraints = (
        constraints.ValueRangeConstraint(0, 4294967295L),
    )

class Opaque(univ.OctetString):
    """SNMP OPAQUE object
    """
    # Explicit tagging    
    tagClass = tagClasses['APPLICATION']
    tagId = 0x04
    tagCategory = 'EXPLICIT'

class Sequence(univ.Sequence):
    """SNMP Sequence
    """
    pass

class SequenceOf(univ.SequenceOf):
    """SNMP SequenceOf
    """
    pass

class Choice(univ.Choice):
    """ASN.1 CHOICE clause
    """
    pass

class NetworkAddress(Choice):
    """SMI NetworkAddress
    """
    choiceNames = [ 'internet' ]
    choiceComponents = [ IpAddress ]

    # Initialize to Internet address
    initialComponent = choiceComponents[0]

class ObjectName(ObjectIdentifier):
    """Names of objects in MIB
    """
    pass

class SimpleSyntax(Choice):
    """Simple (non-constructed) objects
    """
    choiceNames = [ 'number', 'string', 'object', 'empty' ]
    choiceComponents = [ Integer, OctetString, ObjectIdentifier, Null ]
    initialComponent = Null

class ApplicationSyntax(Choice):
    """Constructed objects
    """
    choiceNames = [ 'address', 'counter', 'gauge', 'ticks', 'arbitrary' ]
    choiceComponents = [ NetworkAddress, Counter, Gauge, TimeTicks, Opaque ]

class ObjectSyntax(Choice):
    """Syntax of objects in MIB
    """
    class TableSyntax(Choice):
        choiceNames = [ 'table', 'row' ]
        choiceComponents = [ SequenceOf, Sequence ]
    choiceNames = [ 'simple', 'application_wide', 'sequence' ]
    choiceComponents = [ SimpleSyntax, ApplicationSyntax, TableSyntax ]
    initialComponent = SimpleSyntax
