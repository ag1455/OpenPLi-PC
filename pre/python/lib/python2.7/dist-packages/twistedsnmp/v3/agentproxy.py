"""Client/manager side object for querying Agent via PySNMP v3"""
from twisted.internet import defer, reactor
from twisted.python import failure
from twistedsnmp.pysnmpproto import v2c,v1, error, oid, cacheOIDEncoding
from twistedsnmp.pysnmpproto import CAN_CACHE_OIDS, USE_STRING_OIDS
from twistedsnmp.pysnmpproto import resolveVersion
from twistedsnmp import datatypes, tableretriever
import traceback, socket
from twistedsnmp.logs import agentproxy_log as log

OID = oid.OID

__metaclass__ = type
DEFAULT_BULK_REPETITION_SIZE = 128

class AgentProxy:
	"""Proxy object for querying a remote agent with PySNMP 3.x
	
	This version of the Agent Proxy uses PySNMP or PySNMP-se 3.x to perform
	queries.  It is considerably faster than the PySNMP 4.x equivalent.
	"""
	verbose = 0
	CACHE = {}
	if CAN_CACHE_OIDS:
		cacheOIDEncoding = cacheOIDEncoding
	def __init__(
		self, ip, port=161, 
		community='public', snmpVersion = '1', 
		protocol=None, allowCache = False,
	):
		"""Initialize the SNMPProtocol object

		ip -- ipAddress for the protocol
		port -- port for the connection
		community -- community to use for SNMP conversations
		snmpVersion -- '1' or '2', indicating the supported version
		protocol -- SNMPProtocol object to use for actual connection
		allowCache -- if True, we will optimise queries for the assumption
			that we will be sending large numbers of identical queries 
			by caching every request we create and reusing it for all 
			identical queries.  This means you cannot hold onto the 
			requests, which isn't a problem if you're just using the 
			proxy through the published interfaces.
		"""
		self.ip = str(ip)
		self.port = int(port or 161)
		self.community = str(community)
		self.snmpVersion, self.implementation = self.resolveVersion( snmpVersion)
		self.protocol = protocol
		self.allowCache = allowCache
	resolveVersion = staticmethod( resolveVersion )
	def __repr__( self ):
		"""Get nice string representation of the proxy"""
		ip,port,community,snmpVersion,protocol = self.ip,self.port,self.community,self.snmpVersion,self.protocol
		className = self.__class__.__name__
		try:
			snmpVersionName = snmpVersion.__name__
		except AttributeError:
			snmpVersionName = snmpVersion
		return """%(className)s(%(ip)s,%(port)s,%(community)s,%(snmpVersionName)s,%(protocol)r)"""%locals()
	def get(self, oids, timeout=2.0, retryCount=4):
		"""Retrieve a single set of OIDs from the remote agent

		oids -- list of dotted-numeric oids to retrieve
		retryCount -- number of retries
		timeout -- initial timeout, is multipled by 1.5 on each
			timeout iteration.

		return value is a defered for an { oid : value } mapping
		for each oid in requested set

		XXX Should be raising an error if the response has an
		error message, will raise error if the connection times
		out.
		"""
		if not self.protocol:
			raise ValueError( """Expected a non-null protocol object! Got %r"""%(protocol,))
		oids = [OID(oid) for oid in oids ]
		try:
			request = self.encode(oids, self.community)
			key = self.getRequestKey( request )
			self.send(request.encode())
		except socket.error, err:
			return defer.fail(failure.Failure())
		def asDictionary( value ):
			try:
				return dict(value)
			except Exception, err:
				log.error( """Failure converting query results %r to dictionary: %s""", value, err )
				return {}
		df = defer.Deferred()
		df.addCallback( self.getResponseResults )
		df.addCallback( asDictionary )
		timer = reactor.callLater(timeout, self._timeout, key, df, oids, timeout, retryCount)
		self.protocol.requests[key] = df, timer
		return df
	def set( self, oids, timeout=2.0, retryCount=4):
		"""Set a variable on our connected agent

		oids -- dictionary of oid:value pairs, or a list of
			(oid,value) tuples to be set on the agent

		raises errors if the setting fails
		"""
		if not self.protocol:
			raise ValueError( """Expected a non-null protocol object! Got %r"""%(protocol,))
		if hasattr( oids, "items"):
			oids = oids.items()
		request = self.encode(oids, self.community, set=1)
		key = self.getRequestKey( request )
		def raiseOnError( response ):
			pdu = response.apiGenGetPdu()
			if pdu.apiGenGetErrorStatus():
				raise error.ProtoError( """Set failure""", pdu.apiGenGetErrorStatus() )
			return response
		try:
			self.send(request.encode())
		except socket.error, err:
			return defer.fail(failure.Failure())
		df = defer.Deferred()
		df.addCallback( raiseOnError )
		timer = reactor.callLater(
			timeout, self._timeout, key, df,
			oids, timeout, retryCount,
		)
		self.protocol.requests[key] = df, timer
		return df
		
	def getTable(
		self, roots, includeStart=0,
		recordCallback=None,
		retryCount=4, timeout= 2.0,
		maxRepetitions= DEFAULT_BULK_REPETITION_SIZE,
		startOIDs=None,
	):
		"""Convenience method for creating and running a TableRetriever

		roots -- root OIDs to retrieve
		includeStart -- whether to include the starting OID
			in the set of results, by default, return the OID
			*after* the root oids.
			Note:  Only implemented for v1 protocols, and likely
				to be dropped eventually, as it seems somewhat
				superfluous.
		recordCallback -- called for each new record discovered
			recordCallback( root, oid, value )
		retryCount -- number of retries
		timeout -- initial timeout, is multipled by 1.5 on each
			timeout iteration.
		maxRepetitions -- size for each block requested from the
			server, i.e. how many records to download at a single
			time
		startOIDs -- optional OID markers to be used as starting point,
			i.e. if passed in, we retrieve the table from startOIDs to
			the end of the table excluding startOIDs themselves, rather 
			than from roots to the end of the table.

		Will use bulk downloading when available (i.e. if
		we have implementation v2c, not v1).

		return value is a defered for a { rootOID: { oid: value } } mapping
		"""
		log.debug(
			'getTable( %r, %r, %r, %r, %r, %r )',
			roots, includeStart, recordCallback, retryCount,
			timeout, maxRepetitions,
		)
		if not self.protocol:
			raise ValueError( """Expected a non-null protocol object! Got %r"""%(self.protocol,))
		roots = [OID(oid) for oid in roots ]
		if startOIDs:
			if len(startOIDs) != len(roots):
				raise ValueError( """startOIDs not the same length as roots: %s %s"""%(
					startOIDs, roots,
				))
			if USE_STRING_OIDS:
				# need the isaprefix method, so need real ObjectIdentifier in
				# older PySNMP implementations
				# XXX regression here for PySNMP-non-se!
				rOID = self.getImplementation().ObjectIdentifier
			else:
				rOID = OID
			startOIDs = [rOID(oid) for oid in startOIDs]
			for index,(root,oid) in enumerate(zip( roots, startOIDs )):
				if not rOID(root).isaprefix(oid):
					raise ValueError(
						"""startOID %s (index %s) is not a prefix of root %s: %s"""%(
							oid, index, index, root,
						)
					)
		retriever = tableretriever.TableRetriever(
			self, roots, includeStart=includeStart,
			retryCount=retryCount, timeout= timeout,
			maxRepetitions = maxRepetitions,
		)
		if self.verbose:
			retriever.verbose = 1
		return retriever( recordCallback = recordCallback,startOIDs = startOIDs,)
	
	def dispatchTrap(
		self, message 
	):
		"""Dispatch incoming trap message to any registered watchers..."""
		
	def listenTrap( 
		self, ipAddress=None, genericType=None, specificType=None,
		community=None, 
		callback=None,
	):
		"""Listen for incoming traps, direct to given callback 
		
		ipAddress -- address from which to allow messages
		genericType, specificType -- if present, only messages with the given 
			type are passed to the callback 
		community -- if present, only messages with this community string are
			accepted/passed on to the callback 
		callback -- callable object to register, or None to deregister
		"""
		log.debug( 'listening for trap: %s %s', genericType, specificType )
		trapWatchers = getattr( self.protocol, '_trapRegistry', None )
		if trapWatchers is None:
			trapWatchers = self.protocol._trapRegistry = {}
		generics = trapWatchers.get( ipAddress )
		if generics is None:
			trapWatchers[ ipAddress ] = generics = {} 
		specifics = generics.get( genericType )
		if specifics is None:
			generics[ genericType ] = specifics = {}
		callbacks = specifics.get( specificType )
		if callbacks is None:
			specifics[ specificType ] = callbacks = {}
		callbacks[ community ] = callback 
	
	def send(self, request):
		"""Send a request (string) to the network"""
		return self.protocol.send(request, (self.ip, self.port))

	## Utility methods...
	def getImplementation( self ):
		"""Get the implementation module for this request

		returns v2c or v1 pysnmp modules depending on our
		snmpVersion property.
		"""
		return self.implementation
	def getRequestKey( self, request ):
		"""Get the request key from a request/response"""
		return self.protocol.getRequestKey( request, (self.ip, self.port) )
	def encode(
		self, oids, community,
		next=0, bulk=0, set=0,
		maxRepetitions=DEFAULT_BULK_REPETITION_SIZE,
		# tables suppress all caching for requests past first...
		allowCache = True,
	):
		"""Encode a datagram message
		
		oids -- list of OID instances (where set is False) to be retrieved
				*or*
			list of (OID,value) instances to be assigned
		community -- community string for the query/set
		next -- whether this is to be a getnext query 
		bulk -- whether this is to be a getbulk query
		maxRepetitions -- max number of repeating values for getbulk
		allowCache -- if True, and self.allowCache and not set,
			then we will store and re-use request objects.  allowCache is 
			used by the  tabular retrieval code to avoid caching queries 
			beyond the first, as these are likely to be highly variable.
		"""
		log.debug(
			'encode( %r, %r, %r, %r, %r, %r )',
			oids, community, next, bulk, set, maxRepetitions,
		)
		doCache = allowCache and self.allowCache and (not set)
		if doCache:
			if bulk:
				pduKey = 'get_bulk_request'
			elif next:
				pduKey = 'get_next_request'
			else:
				pduKey = 'get_request'
			cacheKey = pduKey,tuple(oids),community,self.snmpVersion,maxRepetitions
			request = self.CACHE.get( cacheKey )
			if request is not None:
				# this is hacky, initialValue is the incrementer for the global value
				pdu = request['pdu'][pduKey]
				#current = pdu['request_id'].get()
				pdu['request_id'].inc(1)
				#assert pdu['request_id'].get() == current + 1, (pdu['request_id'].get(),current+1)
				return request
		implementation = self.getImplementation()
		if bulk:
			request = implementation.GetBulkRequest()
			request.apiGenGetPdu().apiGenSetMaxRepetitions( maxRepetitions )
		elif set:
			request = implementation.SetRequest()
		elif next:
			request = implementation.GetNextRequest()
		else:
			request = implementation.GetRequest()

		request.apiGenSetCommunity( community )
		pdu = request.apiGenGetPdu()

		if set:
			variables = [ 
				(oid,datatypes.typeCoerce( value, implementation ))
				for oid,value in oids 
			]
		else:
			variables = [(oid,None) for oid in oids]
		
		pdu.apiGenSetVarBind(variables)
		if doCache:
			self.CACHE[ cacheKey ] = request
		return request
	def getResponseResults( self, response ):
		"""Get [(oid,value)...] list from response

		This callback is part of the callback chain for get
		response processing.  In essence, if you have a callback
		that wants [(oid,value)...] format instead of response
		objects register this callback before the needy callback.
		"""
		log.debug( 'getResponseResults( %r )', response )
		if response and not response.apiGenGetPdu().apiGenGetErrorStatus():
			pdu = response.apiGenGetPdu()
			answer = pdu.apiGenGetVarBind()
			return [
				(OID(a),b.getTerminal().get())
				for a,b in answer
				if not isinstance( b, v2c.EndOfMibView)
			]
		return []
	def _timeout(self, key, df, oids, timeout, retryCount):
		try:
			try:
				del self.protocol.requests[ key ]
			except KeyError:
				pass
			if not df.called:
				log.debug( 'timeout check %r', self )
				if retryCount:
					timeout *= 1.5
					retryCount -= 1
					log.debug( 'timeout retry %r %r %r', self, timeout, retryCount )
					request = self.encode(oids, self.community)
					key = self.getRequestKey( request )
					try:
						self.send(request.encode())
					except socket.error, err:
						df.errback( failure.Failure() )
						return
					else:
						timer = reactor.callLater(
							timeout,
							self._timeout, key, df, oids, timeout, retryCount
						)
						self.protocol.requests[key] = df, timer
						return
				log.debug( """timeout raising error: %r""", self )
				df.errback(defer.TimeoutError('SNMP request timed out'))
		except Exception, err:
			df.errback( failure.Failure() )
		
