"""Stand-in module for those without the speed-enhanced tuple-OID implementation"""
USE_STRING_OIDS = True

def OID( value ):
	"""Null function to pretend to be oid.OID"""
	return str(value)

