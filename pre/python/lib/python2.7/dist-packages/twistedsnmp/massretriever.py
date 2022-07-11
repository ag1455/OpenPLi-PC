"""Utility mechanism to retrieve OIDs/tables from large numbers of agents"""
from __future__ import generators, nested_scopes
from twisted.internet import defer, reactor, error
from twisted.python import failure
from twistedsnmp import agentproxy
import traceback
from twistedsnmp.logs import massretriever_log as log

from twistedsnmp.pysnmpproto import oid


def proxies( protocol, addresses, proxyClass=agentproxy.AgentProxy ):
	"""Given protocol and set of addresses, construct AgentProxies

	protocol -- SNMPProtocol instance
	addresses -- tuples of (ip,port,[community,[version]]) to be
		passed to the AgentProxy constructor.
	proxyClass -- the proxy class to use for the retrieval
	"""
	return [
		agentproxy.AgentProxy( protocol=protocol, *args )
		for args in addresses
	]

class MassRetriever( object ):
	"""Table for retrieving value sets from multiple agents

	The object wraps a single query, it cannot be shared among
	multiple queries!
	"""
	def __init__(
		self, proxies,
	):
		"""Initialise the retriever with client AgentProxies

		proxies -- sequence of properties to query in batches
		"""
		self.proxies = proxies
		self.partialDefers = []
		
	def __call__(
		self, oids=(), tables=(), iterDelay=0.005, *arguments, **named
	):
		"""Do mass retrieval of oids and tables from our proxies

		oids -- individual (get) oids for each Agent
		tables -- multi-value (getTable) oids for each Agent
		** named -- passed to proxy object's get and getTable
			methods, so retryCount and timeout can be specified

		returns a DeferredList with the results of all queries
		raises ValueError if no proxies, or neither oids or tables

		The DeferredList's callback recieves a set mapping:
			{ (ip,port) : valueSet }
		where valueSet is a set mapping:
			{ queriedOID : dataValues }
		where dataValues is as returned from get/getTable on the
		proxy object.

		Register callbacks on the DeferredList to recieve a set of
		results in (success,result) format, where success is a boolean
		and result is either the result or an ErrBack object.
		"""
		if not self.proxies:
			raise ValueError( """No AgentProxies specified from which to retrieve""" )
		if not oids and not tables:
			raise ValueError( """Nothing specified to be retrieved""" )
		self.result = {}
		self.finalDefer = defer.Deferred()
		self._arguments = arguments
		self._namedArguments = named
		self.smallBatch( oids, tables, iterDelay=iterDelay )
		return self.finalDefer
		
	def smallBatch( self, oids, tables, index=0, iterDelay=.01 ):
		"""Do single-proxy batches iteratively

		This is the most robust algorithm I've come up with so far,
		it has the rather poor feature of limiting queries to
		1/iterDelay per sec at maximum, but it avoids the annoying problems
		which crop up using nonBatch or proxyBatch implementations.

		Practically speaking, systems seem quite capable of servicing
		a few thousand requests/sec if there's enough processing power,
		but twisted's strange performance characteristics make it
		difficult to write a beast that works to that level AFAICS.
		"""
		if not self.finalDefer.called:
			if index < len(self.proxies):
				proxy = self.proxies[index]
				self.singleProxy(
					proxy,oids,tables
				)
				reactor.callLater( iterDelay, self.smallBatch, oids, tables, index+1 )
			else:
				dl = defer.DeferredList( self.partialDefers )
				dl.addCallback( self.returnFinal )

	def returnFinal( self, dataList ):
		"""Handle final defer callback from completion of all partialDefers

		When all proxies have completed (successfully or not), we callback
		our finalDefer to let our client know about our status.  finalDefer
		gets a pointer to self.result, and the method also returns
		self.result, just for good measure.
		"""
		if not self.finalDefer.called:
			self.finalDefer.callback( self.result )
		# we're just discarding all the failure/success statistics here
		return self.result

	def singleProxy( self, proxy, oids, tables ):
		"""Add configured callbacks for a given agent proxy

		proxy -- the proxy to be queried
		oids -- single oids to be queried (get)
		tables -- multi-value oids to be queried (getTable)
		"""
		if oids:
			d = proxy.get( oids, *self._arguments, **self._namedArguments )
			d.addCallback( self.integrateSingleResult, proxy=proxy )
			d.addErrback( self.handleSingleError, oids=oids, proxy=proxy )
			self.partialDefers.append( d )
		if tables:
			d = proxy.getTable( tables, *self._arguments, **self._namedArguments )
			d.addCallback( self.integrateSingleResult, proxy=proxy )
			d.addErrback( self.handleSingleError, oids=tables, proxy=proxy )
			self.partialDefers.append( d )
	successCount = 0
	def integrateSingleResult( self, value, proxy ):
		"""Integrate single agent-query result into mega-result

		value -- dictionary value as returned from get/getTable
			of the proxy object
		proxy -- the proxy which was used to retrieve the value

		returns value, if a pre-existing dictionary for proxy
		(determined by ip,port) exists, updates that dictionary
		with the new values, otherwise creates a new dictionary
		and updates that.

		Note: Implication here is that, if two proxies for the
			same ip and port are being scanned, their results
			will comingle, and potentially overwrite one another.
		"""
		self.successCount += 1
		log.info( 'success %r', proxy )
		log.debug( '  success value %r: %r', proxy, value )
		self.printStats()
		key = proxy.ip,proxy.port
		set = self.result.get( key )
		if set is None:
			self.result[key] = set = {}
		set.update( value )
		return value
	errorCount=0
	def handleSingleError( self, err, oids, proxy ):
		"""Handle single-agent error by making result[key][oid] None

		err -- handle complete failure of a single proxy to retrieve
			values.
		oids -- the oids being queried
		proxy -- the proxy being queried

		Values are added to the (ip,port) dictionary for the proxy
		with value None iff the root OID does not already exist in
		the dictionary.

		returns None
		"""
		self.errorCount = self.errorCount + 1
		log.info( 'Error: %r %s', proxy, err )
		self.printStats()
		if isinstance( err, failure.Failure ):
			actualError = err.value
			trace = err.getTraceback()
		else:
			actualError = err
			trace = log.getException( err )
		if not isinstance( actualError, error.TimeoutError ):
			log.error(
				"""Retrieval for proxy %r encountered unexpected error: %s""",
				proxy, trace,
			)
		if isinstance( err, (KeyboardInterrupt,SystemExit) ):
			if not self.finalDefer.called:
				self.finalDefer.errback( err )
			return None
		key = proxy.ip,proxy.port
		set = self.result.get( key )
		if set is None:
			self.result[key] = set = {}
		for oidObject in oids:
			oidObject = oid.OID( oidObject )
			if not set.has_key( oidObject ):
				set[oidObject] = None
		return None
	def printStats( self ):
		"""Print heuristic stats for the retriever"""
		log.info(
			'errors=%s success=%s total=%s',
			self.errorCount,
			self.successCount,
			len(self.partialDefers),
		)
