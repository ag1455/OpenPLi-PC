"""Errors specific to TwistedSNMP"""
noError = 0
tooBig = 1 # Response message would have been too large
noSuchName = 2 #There is no such variable name in this MIB
badValue = 3 # The value given has the wrong type or length

class OIDNameError( NameError ):
	"""An OID was specified which is not defined in namespace"""
	def __init__( self, oid, errorIndex=-1 , errorCode=noSuchName, message=""):
		"""Initialise the OIDNameError"""
		self.oid, self.errorIndex, self.errorCode, self.message = oid, errorIndex, errorCode, message
	def __repr__( self ):
		"""Represent the OIDNameError as a string"""
		return """%s( %r, %s, %s, %r )"""%(
			self.__class__.__name__,
			self.oid,
			self.errorIndex,
			self.errorCode,
			self.message,
		)
	__str__ = __repr__

