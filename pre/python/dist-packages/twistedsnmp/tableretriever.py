"""Helper object for the AgentProxy object"""
from twisted.internet import defer, protocol, reactor
from twisted.python import failure
from twistedsnmp.pysnmpproto import v2c,v1, error, oid, USE_STRING_OIDS
import traceback, socket, weakref
from twistedsnmp.logs import tableretriever_log as log

class TableRetriever( object ):
	"""Object for retrieving an entire table from an SNMP agent

	This is the (loose) equivalent of the SNMPWalk examples in
	pysnmp.  It also includes the code for the SNMPBulkWalk, which
	is a generalisation of the SNMPWalk code.
	"""
	# By default, we always try to use bulk retrieval, as
	# it's so much faster if it's available.  Set to 0 to always
	# use iterative retrieval even on v2c ports.
	bulk = 1
	finished = 0

	def __init__(
		self, proxy, roots, includeStart=0,
		retryCount=4, timeout= 2.0,
		maxRepetitions=128,
	):
		"""Initialise the retriever

		proxy -- the AgentProxy instance we want to use for
			retrieval of the data
		roots -- root OIDs to retrieve
		includeStart -- whether to include the starting OID
			in the set of results, by default, return the OID
			*after* the root oids
		retryCount -- number of retries
		timeout -- initial timeout, is multipled by 1.5 on each
			timeout iteration.
		maxRepetitions -- max records to request with a single
			bulk request
		"""
		self.proxy = proxy
		self.roots = [ oid.OID(r) for r in roots]
		self.includeStart = includeStart
		self.retryCount = retryCount
		self.timeout = timeout
		self.values = {} # {rootOID: {OID: value}} mapping
		self.maxRepetitions = maxRepetitions
	def __call__( self, recordCallback=None, startOIDs=None ):
		"""Collect results, call recordCallback for each retrieved record

		recordCallback -- called for each new record discovered
		startOIDs -- optional OID markers to be used as starting point,
			i.e. if passed in, we retrieve the table from startOIDs to
			the end of the table.

		Will use bulk downloading when available (i.e. if
		we have implementation v2c, not v1) and self.bulk is true.

		return value is a defered for a { rootOID: { oid: value } } mapping
		"""
		self.recordCallback = recordCallback
		self.df = defer.Deferred()
		self.getTable( includeStart= self.includeStart, oids=startOIDs, firstCall=True)
		return self.df
	if USE_STRING_OIDS:
		def integrateNewRecord( self, oidValues, rootOIDs ):
			"""Integrate a record-set into the table

			This method is quite simplistic in its approach, it
			just checks for each value in oidValues if it is a
			child or a root in rootOIDs, and if it is, adds it to
			the result-set for that root.  This approach is a
			little more robust than the previous one, which used
			the standard's rather complex mechanism for mapping
			root:oid, and was resulting in some very strange results
			in certain testing situations.
			"""
			OID = self.proxy.getImplementation().ObjectIdentifier
			for root in rootOIDs:
				root = str(root)
				rootOID = OID( root )
				for (key,value) in oidValues:
					key = str(key)
					if rootOID.isaprefix(key) and not isinstance(value, v2c.EndOfMibView):
						current = self.values.get( root )
						if current is None:
							self.values[ root ] = current = {}
						# avoids duplicate callbacks!
						if not current.has_key( key ):
							current[ key ] = value
							if self.recordCallback is not None and callable(self.recordCallback):
								self.recordCallback( root, key, value )
			if self.finished and self.finished < 2:
				self.finished = 2
				if getattr(self,'df',None) and not self.df.called:
					reactor.callLater( 0, self.df.callback, self.values )
					del self.df
	else:
		def integrateNewRecord( self, oidValues, rootOIDs ):
			"""Integrate a record-set into the table

			This method is quite simplistic in its approach, it
			just checks for each value in oidValues if it is a
			child or a root in rootOIDs, and if it is, adds it to
			the result-set for that root.  This approach is a
			little more robust than the previous one, which used
			the standard's rather complex mechanism for mapping
			root:oid, and was resulting in some very strange results
			in certain testing situations.
			"""
			OID = oid.OID
			callback = None
			if self.recordCallback and callable( self.recordCallback ):
				callback = self.recordCallback
			values = self.values
			remainder = oidValues
			# This is still fairly inefficient, but at least we're no longer 
			# N*M iterations, so given the weight of the isaprefix check we 
			# should be faster than before
			for rootOID in rootOIDs:
				unmatched = []
				for (key,value) in remainder:
					key = OID(key)
					if rootOID.isaprefix(key) and not isinstance(value, v2c.EndOfMibView):
						current = values.get( rootOID )
						if current is None:
							values[ rootOID ] = current = {}
						# avoids duplicate callbacks!
						if not current.has_key( key ):
							current[ key ] = value
							if callback is not None:
								callback( rootOID, key, value )
					else:
						unmatched.append( (key,value) )
				remainder = unmatched
			if self.finished and self.finished < 2:
				self.finished = 2
				if getattr(self,'df',None) and not self.df.called:
					reactor.callLater( 0, self.df.callback, self.values )
					del self.df
	def scheduleIntegrate( self, oidValues, rootOIDs ):
		"""Schedule integration of oidValues into this table's results
		
		This breaks up the process so that we can process other events
		before we do the (heavy) work of integrating the result-table...
		"""
		reactor.callLater( 0, self.integrateNewRecord, oidValues, rootOIDs )
		return oidValues
	def getTable(
		self, oids=None, roots=None, includeStart=0,
		retryCount=None, delay=None, firstCall=False,
	):
		"""Retrieve all sub-oids from these roots

		recordCallback -- called for *each* OID:value pair retrieved
			recordCallback( root, oid, value )
		includeStart -- at the moment, only implemented for v1 protocols,
			ignored for v2c.  Should likely be avoided entirely.  Would
			be implemented with a seperate get call anyway, which may as
			well be explicitly coded when you want it.
		firstCall -- whether this is the first call, if it is, and we
			allow caching, we'll ask the proxy to cache our encoded 
			request.  We don't cache continuations because they will
			be different depending on where the iteration happens to
			break.

		This is the "walk" example from pysnmp re-cast...
		"""
		if retryCount is None:
			retryCount = self.retryCount
		if delay is None:
			delay = self.timeout
		if oids is None:
			oids = self.roots
		if roots is None:
			roots = self.roots
		request = self.proxy.encode(
			oids,
			self.proxy.community,
			next= not includeStart,
			bulk = (self.bulk and self.proxy.getImplementation() is v2c),
			maxRepetitions = self.maxRepetitions,
			# only want to cache the first request, as all others are 
			# continuations which might start at any random record
			allowCache = firstCall,
		)

		roots = roots[:]


		try:
			self.proxy.send(request.encode())
		except socket.error, err:
			if retryCount <= 0:
				failObject = failure.Failure()
				if getattr(self,'df',None) and not self.df.called:
					self.df.errback(failObject)
					del self.df
				return
			# wait timeout period before trying again...
			# but reduce timeout period to prevent waiting
			# too long before informing the user of delays...
			delay *= .75
			reactor.callLater(
				self.timeout,
				self.getTable,
				oids, roots, includeStart,
				retryCount-1, delay
			)
			return
		else:
			df = defer.Deferred()
			key = self.proxy.getRequestKey( request )

			df.addCallback( self.areWeDone, roots=roots, request=request )
			df.addCallback( self.proxy.getResponseResults )
			df.addCallback( self.scheduleIntegrate, rootOIDs = roots[:] )
			df.addErrback( self.onProcessingError )

			timer = reactor.callLater(
				self.timeout,
				self.tableTimeout,
				df, key, oids, roots, includeStart, retryCount-1, delay
			)

			self.proxy.protocol.requests[key] = df, timer

			return df
	def onProcessingError( self, reason ):
		"""Deal with a processing error (i.e. an unexpected error condition)"""
		try:
			self.df.errback( reason )
			self.finished = True
			self.df = None
		except defer.AlreadyCalledError, err:
			# we already returned a value... guess we'll log an ignore...
			log.warn(
				"""Processing error encountered after callback triggered: %s""",
				reason.getTraceback(),
			)
		return None
	def tableTimeout( self, df, key, oids, roots, includeStart, retryCount, delay ):
		"""Table timeout implementation

		Table queries timeout if a single retrieval
		takes longer than retryCount * self.timeout
		"""
		if not df.called:
			try:
				if retryCount > 0:
					try:
						if self.proxy.protocol.requests[key][0] is df:
							del self.proxy.protocol.requests[ key ]
					except KeyError:
						pass
					return self.getTable( oids, roots, includeStart, retryCount-1, delay*1.5 )
				try:
					if not self.finished and getattr(self,'df',None):
						self.df.errback( defer.TimeoutError('SNMP request timed out'))
						del self.df
				except defer.AlreadyCalledError:
					pass
			except Exception, err:
				if getattr(self,'df',None) and not self.df.called:
					self.df.errback( err )
					del self.df
				else:
					log.warn(
						"""Unhandled exception %r after request completed, ignoring: %s""",
						log.getException(err),
					)
	def areWeDone( self, response, roots, request, recordCallback=None ):
		"""Callback which checks to see if we're done

		if not, passes on request & schedules next iteration
		if so, returns None
		"""
		log.debug( """areWeDone response: %s""", response )
		newOIDs = response.apiGenGetPdu().apiGenGetVarBind()
		if response.apiGenGetPdu().apiGenGetErrorStatus():
			errorIndex = response.apiGenGetPdu().apiGenGetErrorIndex() - 1
			# SNMP agent (v.1) reports 'no such name' when walk is over
			repeatingRoots = roots[:]
			if response.apiGenGetPdu().apiGenGetErrorStatus() == 2:
				# One of the tables exceeded
				for l in newOIDs, repeatingRoots:
					if errorIndex < len(l):
						del l[errorIndex]
					else:
						raise error.ProtoError('Bad ErrorIndex %s vs length of queried items in VarBind in %s' %( errorIndex, response))
				# okay, now newOIDs is just the set of old OIDs with the
				# exhausted ones removed...
			else:
				errorStatus = str(response['pdu'].values()[0]['error_status'])
				if errorIndex < len(newOIDs):
					raise error.ProtoError(errorStatus + ' at ' + \
										   str(newOIDs[errorIndex][0]))
				raise error.ProtoError(errorStatus)
		else:
			# The following is taken from RFC1905 (fixed not to depend on repetitions)
			# N should be retrieved from the response, the non-repeating set
			# XXX Note, that there seems to be a problem with this
			# algorithm, it assumes that the repeating OID-set remains
			# of constant-size.  AFAICS the spec says it should reduce
			# as each table ends, which makes sense, as you want the remainder
			# of the OIDs to only be those which are still valid at the end
			# of the iteration.

			if isinstance( request, v2c.GetBulkRequest ):
				N = request.apiGenGetPdu().apiGenGetNonRepeaters()
			else:
				N = 0
			assert N == 0, """Not yet sure that non-repeaters are handled correctly!"""
			# R is the number of repeating OIDs
			R = len(roots) - N
			# Leave the last instance of each requested repeating OID
			newOIDs = newOIDs[-R:]

			# Exclude completed var-binds
			repeatingRoots = roots[-R:]
			for idx in range(R):
				try:
					root = self.proxy.getImplementation().ObjectIdentifier(repeatingRoots[idx])
					if (
						not root.isaprefix(newOIDs[idx][0]) or
						isinstance(newOIDs[idx][1], v2c.EndOfMibView)
					):
						# One of the tables exceeded
						for l in newOIDs, repeatingRoots:
							del l[idx]
						break # XXX check logic here, can't more than one end at the same time?
				except IndexError, err:
					raise error.ProtoError( """Incorrectly formed table response: %s : %s"""%(newOIDs,err))

		# Decide whether to request next item...
		if newOIDs and repeatingRoots: # still something to do...
			nextIteration = reactor.callLater(
				0.0,
				self.getTable,
				[x[0] for x in newOIDs],
				roots=repeatingRoots,
				includeStart=0,
			)
		else:
			# actually, this should wait for this last record
			# to get updated before it does the callback :(
			self.finished = 1
		# XXX should return newOIDs with the bad results filtered out
		return response

##class IterTableRetriever( TableRetriever ):
##	"""Iterative version of table retriever 
##	
##	The idea of the iterative table retriever is that it produces new 
##	twined records as they are available, rather than waiting until all 
##	records are loaded to return anything.
##	
##	Produces an overall iterator which generates requests to the agent
##	when its queue of values is no longer full for each root OID being
##	requested.  The iterator returns deferreds, which means there is the
##	potential that the very last iteration may return None in flukeish
##	cases (just happens that the penultimate message precisely ends at 
##	the end of the tables).  In that case the unsatisfied deferreds raise
##	StopIteration in their callbacks...
##	"""
##	fillDeferred = None
##	def __iter__( self ):
##		"""Iterate through the entire table"""
##		while not self.finished:
##			if availableSet():
##				yield defer.succeed( nextSet() )
##			else:
##				if not self.fillDeferred:
##					self.fillDeferred = goFillHopper()
##				df = defer.Deferred()
##				def onResults( result ):
##					if availableSet():
##						df.callback( nextSet() )
##					else:
##						df.errback( StopIteration( """Finished table""" ) )
##				self.fillDeferred.addCallbacks( onResults, onResults )
##				yield df
##	
##	def integrateNewRecord( self, oidValues, rootOIDs ):
##		"""Integrate a record-set into the table
##
##		This method is quite simplistic in its approach, it
##		just checks for each value in oidValues if it is a
##		child or a root in rootOIDs, and if it is, adds it to
##		the result-set for that root.  This approach is a
##		little more robust than the previous one, which used
##		the standard's rather complex mechanism for mapping
##		root:oid, and was resulting in some very strange results
##		in certain testing situations.
##		"""
##		OID = oid.OID
##		callback = None
##		if self.recordCallback and callable( self.recordCallback ):
##			callback = self.recordCallback
##		values = self.values
##		remainder = oidValues
##		# This is still fairly inefficient, but at least we're no longer 
##		# N*M iterations, so given the weight of the isaprefix check we 
##		# should be faster than before
##		for rootOID in rootOIDs:
##			unmatched = []
##			for (key,value) in remainder:
##				key = OID(key)
##				if rootOID.isaprefix(key) and not isinstance(value, v2c.EndOfMibView):
##					current = values.get( rootOID )
##					if current is None:
##						values[ rootOID ] = current = {}
##					# avoids duplicate callbacks!
##					if not current.has_key( key ):
##						current[ key ] = value
##						if callback is not None:
##							callback( rootOID, key, value )
##				else:
##					unmatched.append( (key,value) )
##			remainder = unmatched
##		if self.finished and self.finished < 2:
##			self.finished = 2
##			if getattr(self,'df',None) and not self.df.called:
##				reactor.callLater( 0, self.df.callback, self.values )
##				del self.df
