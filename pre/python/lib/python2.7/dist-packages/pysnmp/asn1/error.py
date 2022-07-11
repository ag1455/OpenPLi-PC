"""Package exception classes"""
from pysnmp import error

class Asn1Error(error.PySnmpError): pass
class BadArgumentError(Asn1Error): pass
class ValueConstraintError(Asn1Error): pass
class NotImplementedError(Asn1Error): pass

