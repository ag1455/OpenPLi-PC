from twisted.python import components

class IAgentProxy(components.Interface):
	"""Proxy object for querying a remote agent"""
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
	def set( self, oids, timeout=2.0, retryCount=4):
		"""Set a variable on our connected agent

		oids -- dictionary of oid:value pairs, or a list of
			(oid,value) tuples to be set on the agent

		raises errors if the setting fails
		"""
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
