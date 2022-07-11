"""In-memory OIDStore based on the standard bisect module"""
from __future__ import generators
import bisect
from twistedsnmp import agent, oidstore, errors
from twistedsnmp.pysnmpproto import v2c,v1, error, oid

try:
	enumerate
except NameError:
	def enumerate( seq ):
		"""Enumerate stand-in for Python 2.2.x"""
		i = 0
		for x in seq:
			yield i,x
			i += 1

if getattr(oid, 'USE_STRING_OIDS',False):
	def oidToSortable( oid ):
		"""Convert a dotted-format OID to a sortable string"""
		return tuple([int(i) for i in oid.split('.') if i ])
	def sortableToOID( sortable ):
		"""Convert sortable rep to a dotted-string representation"""
		return '.%s'%( ".".join([str(x) for x in sortable]))
else:
	oidToSortable = oid.OID
	sortableToOID = oid.OID


class BisectOIDStore(oidstore.OIDStore):
	"""In-memory OIDStore based on the standard bisect module

	This OID store is for use primarily in testing situations,
	where a small OID set is to be loaded and tested against.

	It should be available on any Python installation.

	This is the only storage which allows for chaining
	storages (i.e. inserting a storage as a child of a
	storage) and run-time-calculated values (inserting
	a callable object which calculates values on
	retrieval).

	Signature for a callable value is:
		def callableValue( oid, storage ):
			return finalValue
	"""
	def __init__( self, OIDs=None ):
		"""Initialise the storage with appropriate OIDs"""
		self.OIDs = []
		self.update( OIDs )
	def getExactOID( self, base ):
		"""Get the given OID,value pair for the given base

		This method is responsible for implementing the GET
		request, (or a GETBULK request which specifies
		inclusive operation).
		"""
		base = oidToSortable( base )
		start = bisect.bisect( self.OIDs, (base,) )
		try:
			oid,result = self.OIDs[start]
		except (IndexError,KeyError):
			# do error reporting here
			raise errors.OIDNameError(
				base,
				message="OID not found in database",
			)
		else:
			if oid != base:
				try:
					oid,result = self.OIDs[start-1]
				except IndexError, err:
					pass
				else:
					if (
						oidstore.dumbPrefix( oid, base ) and
						hasattr( result,'getExactOID')
					):
						return result.getExactOID( sortableToOID(base) )
				raise errors.OIDNameError(
					base,
					message="OID not found in database",
				)
			return sortableToOID(base), self.returnValue(result,base)
	
	def setValue( self, oid, value):
		"""Set the given oid,value pair, returning old value

		This method is responsible for implementing the SET
		request.
		"""
		oid = oidToSortable( oid )
		start = bisect.bisect( self.OIDs, (oid,) )
		previousTable = (
			start and self.OIDs and
			oidstore.dumbPrefix( self.OIDs[start-1][0], oid ) and
			hasattr(self.OIDs[start-1][1],'setValue')
		)
		if start < len(self.OIDs):
			oldOID, oldValue = self.OIDs[ start ]
			if oldOID == oid:
				self.OIDs[start] = (oid,value)
				return oldValue
			elif previousTable:
				return self.OIDs[start-1][1].setValue( sortableToOID(oid), value )
		elif previousTable:
			return self.OIDs[start-1][1].setValue( sortableToOID(oid), value )
		self.OIDs.insert( start, (oid,value))
		return None
	def firstOID( self ):
		"""Retrieve the first OID,value pair for the storage

		Raises OIDNameError if there are no pairs available
		"""
		if self.OIDs:
			oid,value = self.OIDs[0]
			if hasattr( value, 'firstOID' ):
				index = 0
				while hasattr( value, 'firstOID' ):
					try:
						return value.firstOID()
					except errors.OIDNameError, err:
						index += 1
						try:
							oid,value = self.OIDs[index]
						except IndexError:
							raise errors.OIDNameError(
								(),
								message="""No OIDs available in this storage""",
							)
			return sortableToOID( oid ), self.returnValue(value,oid)
		else:
			raise errors.OIDNameError(
				(),
				message="""No OIDs available in this storage""",
			)
	def nextOID( self, base ):
		"""Get next OID,value pair after given base OID

		This method is responsible for implementing GETNEXT,
		and GETBULK requests.
		"""
		base = oidToSortable( base )
		start = bisect.bisect( self.OIDs, (base,) )
		# if we have pysnmp-se optimised isaprefix support, use that,
		# as it saves copying the OIDs using slice operations
		if hasattr( base.__class__, 'isaprefix' ):
			dumbPrefix = base.__class__.isaprefix
		else:
			dumbPrefix = oidstore.dumbPrefix
		if start < len( self.OIDs ):
			# require for all OIDs that they precisely match
			# an OID in the OID set we publish...
			oid,value = self.OIDs[start]
			if oid != base and not dumbPrefix( base, oid ):
				raise errors.OIDNameError(
					base,
					message="Could not find OID in database",
				)
			elif oid != base and dumbPrefix( base, oid ):
				# if the found OID is prefixed by key, we want to return this OID
				# otherwise we want to return the *next* item
				
				# iff the value is a sub-storage, we need to get it to
				# see if it's got the proper value within it, if not, then
				# try the next oidstore/value
				if hasattr( value, 'nextOID' ):
					try:
						return value.nextOID( sortableToOID(base) )
					except errors.OIDNameError, err:
						start += 1
			else:
				# otherwise return the item *after* the found OID (exact match)
				# again, if the value is a sub-storage, then we need to search
				# forward from the item after...
				start += 1
			# now get the real value...
			while start < len(self.OIDs ):
				key,value = self.OIDs[start]
				if hasattr( value, 'firstOID' ):
					try:
						return value.firstOID()
					except errors.OIDNameError, err:
						pass
				else:
					return sortableToOID(key),self.returnValue(value,key)
				start += 1
			# overflow error, reached end of our OID table with this OID
			raise errors.OIDNameError( base, message="""OID is beyond end of table""" )
		else:
			# starting OID is beyond end of table
			# only chance is if the last element is a tabular record
			if self.OIDs:
				if (
					hasattr(self.OIDs[-1][1],'nextOID') and
					dumbPrefix( base, self.OIDs[-1][0])
				):
					return self.OIDs[-1][1].nextOID( sortableToOID(base) )
			raise errors.OIDNameError( base, message="""OID is beyond end of table""" )

	def returnValue( self, value, oid ):
		"""Return value, or value.calculateOIDValue( oid, self )"""
		if callable( value ):
			return value( sortableToOID(oid), self )
		return value
