"""API-level exception classes
"""   
from pysnmp.proto import error

class ProtoApiError(error.ProtoError): pass
class BadArgumentError(ProtoApiError): pass
