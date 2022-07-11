"""BSDDB BTree-based Shelve OID Storage"""
import bsddb, shelve, traceback, sys
from twistedsnmp import oidstore, errors, pysnmpproto
import struct, weakref

OID = pysnmpproto.oid.OID

if pysnmpproto.USE_STRING_OIDS:
	def oidToSortable( oid ):
		"""Convert a dotted-format OID to a sortable string"""
		return "".join([
			struct.pack('>I',int(i))
			for i in oid.split('.')
			if i
		])
	def sortableToOID( sortable ):
		"""Convert sortable rep to a dotted-string representation"""
		result = []
		while sortable:
			(i,) = struct.unpack( '>I', sortable[:4])
			result.append( str(i) )
			sortable = sortable[4:]
		return '.%s'%( ".".join(result))
else:
	def oidToSortable( oid ):
		"""Convert a dotted-format OID to a sortable string"""
		return "".join([struct.pack('>I',int(i)) for i in OID(oid)])
	def sortableToOID( sortable ):
		"""Convert sortable rep to a dotted-string representation"""
		result = []
		while sortable:
			(i,) = struct.unpack( '>I', sortable[:4])
			result.append( str(i) )
			sortable = sortable[4:]
		return OID(result)

class Closer( object ):
	"""Close the OIDStore

	This object avoids having a __del__ method defined on the
	OIDStore object, which avoids the potential for memory
	leaks.
	"""
	def __init__( self, client ):
		"""Initialise the closer object"""
		self.btree = client.btree
	def __call__( self ):
		"""Close and cleanup to prevent multiple calls"""
		if self.btree:
			self.btree.close()
			self.btree = None
	def __del__( self ):
		"""Handle deletion of the closer object (close btree if necessary)"""
		self()


class BSDOIDStore(oidstore.OIDStore):
	"""OIDStore implemented using (on-disk) BSDDB files

	This OID store is appropriate for middle-sized OID
	tables which require persistence across Python sessions.
	
	The store uses a BSDDB BTree database provided by the
	Python optional bsddb module wrapped by the standard
	shelve module.
	"""
	def __init__( self, filename, OIDs = None ):
		"""Initialise the storage with appropriate OIDs"""
		self.btree = self.open( filename )
		self.update( OIDs )
		self.close = Closer( self )
	def open( self, filename, mode='c' ):
		"""Open the given shelf as a BSDDB btree shelf

		XXX patches bug in Python 2.3.x set_location for
		bsddb objects as a side-effect
		"""
		if isinstance( filename, (str,unicode)):
			filename = bsddb.btopen( filename, mode )
			if sys.version >= '2.3':
				# need to patch bug in 2.3's set_location
				# XXX need to have a < as well once fixed!
				bsddb._DBWithCursor.set_location = set_location
			filename = shelve.BsdDbShelf( filename )
		return filename
	open = classmethod( open )
	def getExactOID( self, base ):
		"""Get the given OID,value pair for the given base

		This method is responsible for implementing the GET
		request, (or a GETBULK request which specifies
		inclusive operation).
		"""
		encoded = oidToSortable( base )
		if self.btree.has_key( encoded ):
			return base, self.btree[ encoded ]
		raise errors.OIDNameError( base, message="No such OID" )
	def setValue( self, oid, value):
		"""Set the given oid,value pair, returning old value

		This method is responsible for implementing the SET
		request.
		"""
		old = None
		oid = oidToSortable( oid )
		if self.btree.has_key( oid ):
			try:
				old = self.btree[ oid ]
			except KeyError:
				pass
		self.btree[ oid ] = value
		self.btree.sync()
		return old
	def firstOID( self ):
		"""Retrieve the first OID,value pair for the storage

		Raises OIDNameError if there are no pairs available
		"""
		try:
			oid,value = self.btree.first()
			return sortableToOID( oid ), value
		except bsddb.error:
			raise errors.OIDNameError(
				(),
				message="""No OIDs available in this storage""",
			)
	def nextOID( self, base ):
		"""Get next OID,value pair after given base OID

		This method is responsible for implementing GETNEXT,
		and GETBULK requests.
		"""
		try:
			encoded = oidToSortable( base )
			oid, value = self.btree.set_location(encoded)
			oid = sortableToOID( oid )
		except KeyError, err:
			raise errors.OIDNameError(
				base,
				message="OID not found in database"
			)
		if oid == base:
			try:
				oid,value = self.btree.next()
				oid = sortableToOID( oid )
			except KeyError, err:
				raise errors.OIDNameError(
					base,
					message="OID appears to be last in database"
				)
		return oid, value


def set_location(self, key):
	"""Patched version of _DBWithCursor.set_location for Python 2.3.x"""
	self._checkOpen()
	self._checkCursor()
	return self.dbc.set_range(key)
