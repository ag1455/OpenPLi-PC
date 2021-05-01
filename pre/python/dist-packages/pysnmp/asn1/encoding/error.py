"""Package exception classes
"""   
from pysnmp.asn1 import error

class EncodingError(error.Asn1Error): pass
