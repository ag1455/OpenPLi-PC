"""Hack around PySNMP lack of generic types

This was written against PySNMP 3.3.x, apparently 3.4.x has
some fixes to make this all cleaner, but I haven't had time
to revisit the question just yet.
"""
from twistedsnmp.pysnmpproto import v2c,v1,rfc1902

class SimpleConverter:
	"""Simple callable object that just does self.target(value.get())"""
	def __init__( self, target ):
		self.target = target
	def __call__( self, value ):
		return self.target( value.get())

def ipConvert( value ):
	"""Mapping that returns v2c.IpAddress(value.get())"""
	return v2c.IpAddress(value.get())
def nullMapping( value ):
	"""Mapping that just returns value unchanged"""
	return value

v2Mapping = [
	#(v2c.BitString, v1. ),
	#(v2c.Bits, v1. ),
	(int, v1.Integer),
	(str, v1.OctetString),
	(v2c.Choice, SimpleConverter(v1.Choice) ),
	(v2c.Counter32, SimpleConverter(v1.Counter) ),
	(v2c.Counter64, SimpleConverter(v1.Counter) ),
	(v2c.Gauge32, SimpleConverter(v1.Gauge) ),
	(v2c.Integer, SimpleConverter(v1.Integer) ),
	(v2c.Integer32, SimpleConverter(v1.Integer) ),
	(v2c.IpAddress, SimpleConverter(v1.IpAddress) ),
	(v2c.Null, SimpleConverter(v1.Null) ),
	(v2c.ObjectIdentifier, SimpleConverter(v1.ObjectIdentifier) ),
	(v2c.ObjectName, SimpleConverter(v1.ObjectName) ),
	(v2c.OctetString, SimpleConverter(v1.OctetString) ),
	(v2c.Opaque, SimpleConverter(v1.Opaque) ),
	(v2c.Sequence, SimpleConverter(v1.Sequence) ),
##	(v2c.SequenceOf, SimpleConverter(v1.SequenceOf) ),
	(v2c.TimeTicks, SimpleConverter(v1.TimeTicks) ),
	#(v2c.Unsigned32, v1.Integer ),
	(v2c.VarBind, SimpleConverter(v1.VarBind )),
##	(v2c.VarBindList, SimpleConverter(v1.VarBindList) ),
	(v2c.Counter64, SimpleConverter(rfc1902.Counter64)),
]	
v1Mapping = [
	(int, v2c.Integer),
	(str, v2c.OctetString),
	(v1.Choice, SimpleConverter(v2c.Choice)),
	(v1.Counter, SimpleConverter(v2c.Counter32)),
	(v1.Gauge, SimpleConverter(v2c.Gauge32)),
	(v1.Integer, SimpleConverter(v2c.Integer)),
	(v1.IpAddress, SimpleConverter(v2c.IpAddress)),
	#(v1.NetworkAddress, v2c.N),
	(v2c.EndOfMibView, nullMapping),
	(v1.Null, SimpleConverter(v2c.Null)),
	(v1.ObjectIdentifier, SimpleConverter(v2c.ObjectIdentifier)),
	(v1.ObjectName, SimpleConverter(v2c.ObjectName)),
	(v1.ObjectSyntax, SimpleConverter(v2c.ObjectSyntax)),
	(v1.OctetString, SimpleConverter(v2c.OctetString)),
	(v1.Opaque, SimpleConverter(v2c.Opaque)),
	(v1.Sequence, SimpleConverter(v2c.Sequence)),
##	(v1.SequenceOf, SimpleConverter(v2c.SequenceOf)),
	(v1.TimeTicks, SimpleConverter(v2c.TimeTicks)),
	(v1.VarBind, SimpleConverter(v2c.VarBind)),
##	(v1.VarBindList, SimpleConverter(v2c.VarBindList)),
	(rfc1902.Counter64, SimpleConverter(v2c.Counter64)),
]

def typeCoerce( value, implementation ):
	"""Coerce value to implementation-friendly version

	value -- Python or PySNMP value to be represented as a value
		compatible with the implementation given
	implementation -- v1 or v2c modules from PySNMP, they are
		simply used to choose between use of data-type mappings
	"""
	if implementation is v1:
		mapping = v2Mapping
	else:
		mapping = v1Mapping
	for cls, target in mapping:
		if isinstance( value, cls ):
			value = target( value )
			break
	return value
