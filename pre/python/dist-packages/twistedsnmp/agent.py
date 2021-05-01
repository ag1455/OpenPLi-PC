"""SNMP Logic for Agent(Server)-side implementations"""
from __future__ import generators
import weakref
from twistedsnmp import datatypes
from twistedsnmp.pysnmpproto import v2c,v1, error, resolveVersion, oid
from twistedsnmp.errors import noError, tooBig, noSuchName, badValue
from twistedsnmp import errors
from twisted.internet import reactor, defer

__metaclass__ = type

try:
	enumerate
except NameError:
	def enumerate( seq ):
		i = 0
		for x in seq:
			yield i,x
			i += 1

class Agent:
	"""Implementation of SNMP Logic for Agent-side implementations

	This base-class is intended to interact with objects providing
	an OID-store interface.  It's primary purpose is to implement
	the iteration control mechanisms for querying that store.
	"""
	def __init__(self, dataStore, protocol=None):
		"""Initialise the MockAgent with OID list"""
		self.dataStore = dataStore
		self._trapRegistry = {}
		if protocol is not None:
			self.setProtocol( protocol )
			protocol.setAgent( self )
	def setProtocol( self, protocol ):
		"""Set the protocol for the agent object"""
		self.protocol = protocol
	def get( self, request, address, implementation ):
		"""Get OID(s) for the request and return response

		request -- parsed (i.e. object-form) GET request
		address -- (ip,port) Internet address from which the
			request was received.
		implementation -- implementation module for the request,
			i.e. the v2c or v1 module

		sends response to the client as a side effect
		
		returns the sent response
		"""
		variables = request.apiGenGetPdu().apiGenGetVarBind()
		response = request.reply()
		pdu = response.apiGenGetPdu()
		try:
			result = self.getOIDs( [key for (key,_) in variables] )
		except errors.OIDNameError, err:
			pdu.apiGenSetErrorStatus( err.errorCode )
			pdu.apiGenSetErrorIndex( err.errorIndex + 1 ) # 1-indexed
			pdu.apiGenSetVarBind(variables)
			result = None
		else:
			pdu.apiGenSetVarBind([
				(key,datatypes.typeCoerce(value,implementation))
				for (key,value) in result
			])
		self.protocol.send( response.encode(), address )
		return response
	def getOIDs( self, oids ):
		"""Get the given set of OIDs

		oids -- sequence of OIDs to retrieve

		return list of oid,value pairs
		"""
		result = []
		for i,key in enumerate(oids):
			try:
				result.append( self.dataStore.getExactOID( key ) )
			except errors.OIDNameError, err:
				# do error reporting here
				err.errorIndex = i
				raise
		return result
	def getNext( self, request, address, implementation ):
		"""Respond to an iterative get-next request

		request -- parsed (i.e. object-form) GETNEXT request
		address -- (ip,port) Internet address from which the
			request was received.
		implementation -- implementation module for the request,
			i.e. the v2c or v1 module

		sends response to the client as a side effect
		
		returns the sent response

		XXX Doesn't currently check for message too long error
			condition

		(1)  If, for any object name in the variable-bindings field,
			that name does not lexicographically precede the name of
			some object available for get operations in the relevant
			MIB view, then the receiving entity sends to the
			originator of the received message the GetResponse-PDU of
			identical form, except that the value of the error-status
			field is noSuchName, and the value of the error-index
			field is the index of said object name component in the
			received message.

		(2)  If the size of the GetResponse-PDU generated as described
			below would exceed a local limitation, then the receiving
			entity sends to the originator of the received message
			the GetResponse-PDU of identical form, except that the
			value of the error-status field is tooBig, and the value
			of the error-index field is zero.

		(3)  If, for any object named in the variable-bindings field,
			the value of the lexicographical successor to the named
			object cannot be retrieved for reasons not covered by any
			of the foregoing rules, then the receiving entity sends
			to the originator of the received message the
			GetResponse-PDU of identical form, except that the value
			of the error-status field is genErr and the value of the
			error-index field is the index of said object name
			component in the received message.

		If none of the foregoing rules apply, then the receiving protocol
		entity sends to the originator of the received message the
		GetResponse-PDU such that, for each name in the variable-bindings
		field of the received message, the corresponding component of the

		GetResponse-PDU represents the name and value of that object whose
		name is, in the lexicographical ordering of the names of all objects
		available for get operations in the relevant MIB view, together with
		the value of the name field of the given component, the immediate
		successor to that value.  The value of the error-status field of the
		GetResponse-PDU is noError and the value of the errorindex field is
		zero.  The value of the request-id field of the GetResponse-PDU is
		that of the received message.

		http://www.faqs.org/rfcs/rfc1157.html
		Section: 4.1.3, GetNextRequest
		"""
		variables = request.apiGenGetPdu().apiGenGetVarBind()
		response = request.reply()
		pdu = response.apiGenGetPdu()
		try:
			result = self.getNextOIDs( [key for (key,_) in variables] )
		except errors.OIDNameError, err:
			pdu.apiGenSetErrorStatus( err.errorCode )
			pdu.apiGenSetErrorIndex( err.errorIndex + 1 ) # 1-indexed
			pdu.apiGenSetVarBind(variables)
			result = None
		else:
			pdu.apiGenSetVarBind([
				(key,datatypes.typeCoerce(value,implementation))
				for (key,value) in result
			])
		self.protocol.send( response.encode(), address )
		return response
	def getNextOIDs( self, oids ):
		"""Get the given set of OIDs' next items

		oids -- sequence of OIDs from which to retrieve next OIDs

		return list of oid,value pairs
		"""
		result = []
		for index, base in enumerate(oids):
			try:
				result.append( self.dataStore.nextOID( base ))
			except errors.OIDNameError, err:
				errorIndex = index
				raise
		return result

	def getTable( self, request, address, implementation ):
		"""Respond to an all-at-once (v2) get request

		request -- parsed (i.e. object-form) GETBULK request
		address -- (ip,port) Internet address from which the
			request was received.
		implementation -- implementation module for the request,
			i.e. the v2c or v1 module

		sends response to the client as a side effect
		
		returns the sent response

		The get-bulk request has two elements, a set of non-repeating
		get-next OIDs (normally 0), and a set of repeating get-bulk
		OIDs.  Up to a specified number of ordered elements starting
		at the specified OIDs are returned for each of the bulk elements,
		with truncation of the entire set occuring if all tables are
		exhausted (reach the end of the OID tables), otherwise will
		include subsequent table values sufficient to fill in the
		message-size.

		http://www.faqs.org/rfcs/rfc1448.html
		Section 4.2.3, The GetBulkRequest-PDU
		"""
		from twistedsnmp import datatypes
		variables = request.apiGenGetPdu().apiGenGetVarBind()
		result = []
		errorCode = None
		errorIndex = None
		# Get the repetition counts...
		# if < 0, set to 0, though for maxRepetitions we set to 255 since
		# that's the default and 0 would mean no repetitions at all
		# nonRepeaters is the set of OIDs which are treated as get-next
		# requests, while the rest of the query OIDs are get-bulk, repeating
		# up to maxRepetitions times.
		nonRepeaters = max((request.apiGenGetPdu().apiGenGetNonRepeaters(),0))
		maxRepetitions = max((request.apiGenGetPdu().apiGenGetMaxRepetitions(),0)) or 255

		response = request.reply()
		pdu = response.apiGenGetPdu()

		try:
			result = self.getTableOIDs(
				[ oid for (oid,_) in variables[:nonRepeaters] ],
				[ oid for (oid,_) in variables[nonRepeaters:] ],
				maxRepetitions,
			)
		except errors.OIDNameError, err:
			# should never happen, but who knows...
			pdu.apiGenSetErrorStatus( err.errorCode )
			pdu.apiGenSetErrorIndex( err.errorIndex + 1 ) # 1-indexed
			pdu.apiGenSetVarBind(variables)
			result = None
		else:
			pdu.apiGenSetVarBind([
				(key,datatypes.typeCoerce(value,implementation))
				for (key,value) in result
			])
		self.protocol.send( response.encode(), address )
		return response
	def getTableOIDs( self, nonRepeating=(), repeating=(), maxRepetitions=255 ):
		"""Get non-repeating and repeating OID values

		nonRepeating -- sequence of OIDs for non-repeating retrieval
		repeating -- sequence of OIDs for repeating retrieval
		maxRepetitions -- maximum number of repetitions

		Note:
			The interpretation here is that the set of repeating values
			must remain of equal size, that is, our result set must be
			N + (M*r) (where M is the repeating count and r the number of
			iterations) items.  This is new with version 0.3.9, previous
			versions assumed that we would trim the size of the window
			as each starting-oid reached end-of-mib-view, which would result
			in values no longer being indexed to their source OID.

		return list of oid,value pairs
		"""
		# Known as M, N and R in the spec...
		result = []
		for index, base in enumerate(nonRepeating):
			try:
				oid,value = self.dataStore.nextOID( base )
			except errors.OIDNameError, err:
				oid = oid
				value = v2c.EndOfMibView()
			result.append( (oid,value) )
		nextIter = repeating
		for repeat in range(maxRepetitions):
			variables = nextIter
			nextIter = []
			foundGood = 0
			for index, base in enumerate(variables):
				try:
					oid,value = self.dataStore.nextOID( base )
					foundGood = 1
				except errors.OIDNameError, err:
					# XXX is the use of base here correct?
					oid = base
					value = v2c.EndOfMibView()
				nextIter.append( oid )
				result.append( (oid,value) )
			if not foundGood:
				break # just to save processing
		return result
	def set( self, request, address, implementation ):
		"""Set OIDs as given by request

		request -- parsed (i.e. object-form) SET request
		address -- (ip,port) Internet address from which the
			request was received.
		implementation -- implementation module for the request,
			i.e. the v2c or v1 module

		XXX Spec requires a two-stage (or more) commit sequence with
		undo on failure even including the commit itself.  Not
		implemented.
		"""
		errorCode = 0
		errorIndex = 0
		variables = request.apiGenGetPdu().apiGenGetVarBind()
		for index, (oid,value) in enumerate(variables):
			errorCode = self.dataStore.validateSetValue( oid, value, request, address, implementation )
			if errorCode:
				errorIndex = index
				break
		response = request.reply()
		pdu = response.apiGenGetPdu()
		if errorCode:
			pdu.apiGenSetErrorStatus( errorCode )
			pdu.apiGenSetErrorIndex( errorIndex + 1 ) # 1-indexed
			pdu.apiGenSetVarBind(variables)
			return self.protocol.send( response.encode(), address )
		self.setOIDs( variables )
		response = request.reply()
		pdu.apiGenSetVarBind(variables)
		return self.protocol.send( response.encode(), address )
	def setOIDs( self, variables ):
		"""Set the OID:value variables in our dataStore"""
		for index, (oid,value) in enumerate(variables):
			self.dataStore.setValue( oid, value  )
		return variables
	def getSysObjectId( self ):
		"""Get our system object identifier for traps"""
		# XXX find something useful...
		return '1.3.6.1.1.2.3.4.1'


	def registerTrap( 
		self, trapHandler,
	):
		"""Register the given manager to watch the given trap
		
		The key (genericType,specificType) will be used to dispatch trap 
		messages to those managers which are registered here
		
		Note: there is not automated clearing of managers from this table,
		if you need to remove a manager you must call deregisterTrap( )
		"""
		specifics = self._trapRegistry.get( trapHandler.genericType)
		if specifics is None:
			self._trapRegistry[ trapHandler.genericType ] = specifics = {}
		managers = specifics.get( trapHandler.specificType )
		if managers is None:
			specifics[ trapHandler.specificType ] = managers = {}
		managers[ trapHandler.managerIP ] = trapHandler
		return trapHandler
	def findTrapHandlers( self, genericType=None, specificType=None ):
		"""Yield set of paths to handlers for given types"""
		if genericType is None:
			for key in self._trapRegistry.keys():
				if key is not None:
					for path in self.findTrapHandlers( key, specificType ):
						yield path 
		else:
			for gType in (genericType,None):
				specifics = self._trapRegistry.get( gType )
				if specifics:
					if specificType is None:
						for key,value in specifics.items():
							if value:
								yield gType, key, value 
					elif specifics.has_key( specificType ):
						if specifics[ specificType ]:
							yield gType, specificType, specifics[ specificType ]
					elif specifics.has_key( None ):
						if specifics[ None ]:
							yield gType, None, specifics[None]
	
	def deregisterTrap(
		self, managerIP, genericType=None, specificType=None,
	):
		"""Deregister given managerIP from given traps 
		
		genericType -- if None, deregister from all generic types 
		specificType -- if None, deregister from all specific types 
		"""
		count = 0
		for (generic,specific,values) in self.findTrapHandlers(
			genericType, specificType
		):
			if values.has_key( managerIP ):
				try:
					del values[ managerIP ]
					count += 1
				except KeyError, err:
					pass 
				try:
					if not self._trapRegistry[generic][specific]:
						del self._trapRegistry[generic][specific]
				except KeyError, err:
					pass
				try:
					if not self._trapRegistry[generic]:
						del self._trapRegistry[generic]
				except KeyError, err:
					pass
		return count
	def sendTrap(
		self, genericType=6, specificType=0, 
		pdus=None,
	):
		"""Send given trap to all registered watchers"""
		for (generic,specific,values) in self.findTrapHandlers(
			genericType, specificType
		):
			for handler in values.values():
				# XXX need to be able to add more data!
				handler.send( 
					self, 
					genericType=genericType, 
					specificType=specificType, 
					pdus=pdus 
				)

class TrapHandler( object ):
	"""Registration for a given Trap for a given manager"""
	def __init__( 
		self, managerIP, community='public', version='v2c',
		genericType=None, specificType=None,
	):
		"""Initialise the registration for the given parameters
		
		managerIP -- (IP,port) address to which to send messages 
		community -- community string to use for the messages we send 
		genericType -- the major type spec for matching messages
		specificType -- the minor type spec for matching messages
		"""
		self.managerIP = managerIP
		self.community = community
		self.genericType = genericType
		self.specificType = specificType
		self.implementation = resolveVersion( version)[1]
	def send( self, agent, genericType=6, specificType=0, pdus=None ):
		"""Given agent, send our message to the management stations"""
		# XXX pysnmp doesn't seem to support v2 traps...
		from pysnmp.proto.api import alpha
		ver = alpha.v1
		req = ver.Message()
		req.apiAlphaSetCommunity(self.community)
		trap = ver.TrapPdu()
		if ver is alpha.v1:
			trap.apiAlphaSetEnterprise(agent.getSysObjectId())
			trap.apiAlphaSetGenericTrap( genericType )
			trap.apiAlphaSetSpecificTrap( specificType )
			if pdus:
				if hasattr( pdus, 'items' ):
					pdus = pdus.items()
				pdus = [
					(oid.OID(key),datatypes.typeCoerce(value, v1))
					for key,value in pdus 
				]
				trap.apiAlphaSetVarBindList( *pdus )
		else:
			raise NotImplementedError( """No v2c trap-sending support yet""" )
		req.apiAlphaSetPdu(trap)
		return agent.protocol.send( req.berEncode(), self.managerIP )


