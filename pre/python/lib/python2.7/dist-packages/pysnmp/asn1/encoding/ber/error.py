"""
   Package exception classes.

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002.
"""   
from pysnmp.asn1.encoding import error

class BerEncodingError(error.EncodingError):
    """Base class for ber sub-package exceptions
    """
    pass

# Common exceptions

class BadArgumentError(BerEncodingError):
    """Malformed argument
    """
    pass

class TypeMismatchError(BerEncodingError):
    """Type Mismatch Error
    """
    pass

class OverFlowError(BerEncodingError):
    """Data item does not fit the packet
    """
    pass

class UnderRunError(BerEncodingError):
    """Short BER data stream
    """
    pass

class BadEncodingError(BerEncodingError):
    """Incorrect BER encoding
    """
    pass
