"""
   Compatibility exception class

   Written by Ilya Etingof <ilya@glas.net>, 2001, 2002. Suggested by
   Case Van Horsen <case@ironwater.com>.
""" 
import pysnmp.proto.error

class Generic(pysnmp.proto.error.ProtoError):
    """Base class for depricated PySNMP 2.x compatibility API
    """
    pass
