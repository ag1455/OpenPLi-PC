"""PySNMP v4-compatible proxy class"""
__metaclass__ = type
from pysnmp.entity import config
from twisted.internet import defer, reactor
from pysnmp.entity.rfc3413 import cmdgen

DEFAULT_BULK_REPETITION_SIZE = 256

def targetNames( ):
	"""Create an iterable producing monotonously increasing integers"""
	i = 0
	while 1:
		i += 1
		yield i

class BaseProxy:
	"""Base class for all proxies based on SNMP v4.x"""
	_targetCache = {}
	_newTargetName = targetNames().next
	def __init__( self, engine, targetName, snmpVersion='3' ):
		"""Initialize the Proxy object's core parameters"""
		self.engine = engine 
		self.targetName = targetName
		self.snmpVersion = self.resolveVersion( snmpVersion )
	def resolveVersion( self, versionString ):
		"""Resolve to canonical format for version"""
		if versionString in ('1','v1'):
			return '1'
		elif versionString in ('2','2c','v2','v2c'):
			return '2c'
		else:
			return '3'
	def _targetName( self, engine, ip, port, paramName ):
		"""Get/create a target name for given target for given connection name"""
		key = (ip,port,paramName)
		targetName = self._targetCache.get( key )
		if targetName is None:
			nameID = self._newTargetName()
			targetName = 'target-%s'%(nameID,)
			config.addTargetAddr(
				engine, targetName, config.snmpUDPDomain,
				(ip, port), paramName
			)
			self._targetCache[ key ] = targetName
		return targetName
	def get(self, oids, timeout=2.0, retryCount=4):
		"""Retrieve a single set of OIDs from the remote agent

		oids -- list of dotted-numeric oids to retrieve
		retryCount -- number of retries
		timeout -- initial timeout, is multipled by 1.5 on each
			timeout iteration.

		return value is a defered for an { oid : value } mapping
		for each oid in requested set

		XXX Should be raising an error if the response has an
		error message
		"""
		oids = [(oid,None) for oid in oids ]
		df = defer.Deferred( )
		cmdgen.GetCommandGenerator().sendReq(
			self.engine, 
			self.targetName,
			oids,
			self._onGetResult, 
			df
		)
		return df
	def _onGetResult( 
		self, sendRequestHandle, 
		errorIndication, errorStatus, errorIndex,
		varBinds, df
	):
		"""Handle response from remote agent to our request"""
		# If we have an error, call errback on df, otherwise 
		# call callback with the results
		if errorIndication:
			# XXX need differentiation and a common error type...
			df.errback(
				RuntimeError( errorIndication ),
			)
		else:
			df.callback( dict([
				(a,b)
				for a,b in varBinds
				#if not isinstance( b, v2c.EndOfMibView)
			]))
	def _onTimeout( self, df, timeout, retryCount ):
		"""Implement our timeout handling algorithm
		
		Try up to retryCount times to retrieve, on failure,
		we abandon the attempt.
		"""
		# have to get support for this in pysnmp 4.x

	def set( self, oids, timeout=2.0, retryCount=4):
		"""Set a variable on our connected agent

		oids -- dictionary of oid:value pairs, or a list of
			(oid,value) tuples to be set on the agent

		raises errors if the setting fails
		"""
		df = defer.Deferred( )
		cmdgen.SetCommandGenerator().sendReq(
			self.engine, self.targetName,
			oids,
			self._onSetResult, 
			df,
		)
		return df
	def _onSetResult( 
		self, sendRequestHandle, 
		errorIndication, errorStatus, errorIndex,
		varBinds, 
		df,
	):
		if errorIndication:
			df.errback( RuntimeError( errorIndication, errorStatus, errorIndex ))
		else:
			df.callback( dict(varBinds))
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
		df = defer.Deferred( )
		result = {}
		if startOIDs is None:
			startOIDs = roots
		def _onTabularResult( 
			sendRequestHandle, 
			errorIndication, errorStatus, errorIndex,
			varBindTable, df
		):
			"""Process a (partial) tabular result"""
			foundRoots = {}
			foundNonNull = False
			for row in varBindTable:
				foundNonNull = False
				for (key,value) in row:
					if value is not None:
						foundNonNull = True
						for r in roots:
							if key[:len(r)] == r:
								tbl = result.get( r )
								if tbl is None:
									tbl = result[ r ] = {}
								tbl[ key] = value 
								foundRoots[ r ] = key
			if not foundRoots or not foundNonNull:
				df.callback( result )
			else:
				roots[:] = foundRoots.keys()
				if self.snmpVersion != '1':
					cmdgen.BulkCommandGenerator().sendReq(
						self.engine, self.targetName, 
						0, # nonRepeaters (count)
						maxRepetitions,
						[(r,None) for r in foundRoots.values()], # varBinds
						_onTabularResult, 
						df,
					)
				else:
					cmdgen.NextCommandGenerator().sendReq(
						self.engine, self.targetName, 
						[(r,None) for r in foundRoots.values()], 
						_onTabularResult, df
					)
		if self.snmpVersion != '1':
			cmdgen.BulkCommandGenerator().sendReq(
				self.engine, self.targetName, 
				0, # nonRepeaters (count)
				maxRepetitions,
				[(r,None) for r in startOIDs], # varBinds
				_onTabularResult, 
				df,
			)
		else:
			cmdgen.NextCommandGenerator().sendReq(
				self.engine, self.targetName, 
				[(r,None) for r in startOIDs], 
				_onTabularResult, df
			)
		return df
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


class AgentProxy(BaseProxy):
	"""Proxy object for querying a remote agent"""
	_v1ParamCache = {}
	_newV1Name = targetNames().next
	def __init__(
		self, ip, port=161, 
		community='public', snmpVersion = '1', 
		engine=None, allowCache = False,
	):
		"""Initialize the SNMPProtocol object

		ip -- ipAddress to which we connect
		port -- remote port for the connection
		
		community -- community to use for SNMP v1 or v2c conversations
		snmpVersion -- '1', '2' or 3, indicating the supported SNMP version
		
		engine -- configured PySNMP v4 engine
		securityName -- name by which our connection parameters are known
			if not provided, autogenerated
		authProtocol -- authorisation protocol used to connect 
		authKey -- authorisation key used to connect
		privProtocol -- protocol used to obscure requests from viewers
		privKey -- key used to obscure requests
		
		allowCache -- if True, we will optimise queries for the assumption
			that we will be sending large numbers of identical queries 
			by caching every request we create and reusing it for all 
			identical queries.  This means you cannot hold onto the 
			requests, which isn't a problem if you're just using the 
			proxy through the published interfaces.
		"""
		targetName = self.v1TargetName(
			engine,
			ip, port=port, 
			community=community, 
			snmpVersion=snmpVersion,
		)
		super( AgentProxy, self ).__init__( engine, targetName,snmpVersion )
		self.ip = str(ip)
		self.port = int(port or 161)
		self.community = str(community)
		self.snmpVersion = snmpVersion
		self.allowCache = allowCache
	def v1TargetName( 
		self, engine,
		ip, port=161, 
		community='public', 
		snmpVersion='2',
	):
		"""Find/create target name for v1/v2 connection to given agent"""
		key = (community,snmpVersion=='1')
		paramName = self._v1ParamCache.get( key )
		if paramName is None:
			nameID = self._newV1Name()
			name = 'v1sys-%s'%(nameID)
			config.addV1System(engine, name, community)
			paramName = 'v1param-%s'%(nameID)
			if snmpVersion == '1':
				version = 0
			else:
				version = 1
			config.addTargetParams(
				engine, paramName, name, 'noAuthNoPriv', version
			)
			self._v1ParamCache[ key ] = paramName
		return self._targetName( engine, ip, port, paramName )

class V3Proxy(BaseProxy):
	"""Proxy object for querying a remote agent using SNMP version 3"""
	AUTH_PROTOCOL_REGISTRY = {
		'MD5': config.usmHMACMD5AuthProtocol,
		'SHA': config.usmHMACSHAAuthProtocol,
		None: config.usmNoAuthProtocol,
		'': config.usmNoAuthProtocol,
		False:config.usmNoAuthProtocol,
	}
	PRIV_PROTOCOL_REGISTRY = {
		'DES': config.usmDESPrivProtocol,
		None: config.usmNoPrivProtocol,
		'': config.usmNoPrivProtocol,
		False:config.usmNoPrivProtocol,
	}
	_v3paramCache = {}
	_newV3Name = targetNames().next
	def __init__(
		self, ip, port=161, 
		engine=None, 
		authKey=None,
		privKey=None,
		authProtocol='MD5',
		privProtocol='DES',
		allowCache = False,
	):
		"""Initialize the Proxy object

		ip -- ipAddress to which we connect
		port -- remote port for the connection
		
		engine -- configured PySNMP v4 engine
		authKey -- authorisation key used to connect
		privKey -- key used to obscure requests
		authProtocol -- authorisation protocol used to connect 
		privProtocol -- protocol used to obscure requests from viewers
		
		allowCache -- if True, we will optimise queries for the assumption
			that we will be sending large numbers of identical queries 
			by caching every request we create and reusing it for all 
			identical queries.  This means you cannot hold onto the 
			requests, which isn't a problem if you're just using the 
			proxy through the published interfaces.
		"""
		targetName = self.v3TargetName(
			ip, port=port, 
			authKey=authKey,
			privKey=privKey,
			authProtocol=authProtocol,
			privProtocol=privProtocol,
		)
		super( V3Proxy, self ).__init__( engine, targetName, snmpVersion='3' )
		self.ip = str(ip)
		self.port = int(port or 161)
		self.snmpVersion = '3'
		self.allowCache = allowCache
	def v3TargetName( 
		self, engine,
		ip, port=161, 
		authKey=None,
		privKey=None,
		authProtocol='MD5',
		privProtocol='DES',
	):
		"""Find/create target name for v1/v2 connection to given agent
		
		authProtocol -- one of None, 'MD5' or 'SHA' determining the hashing
			of the authorisation key (password)
		privProtocol -- one of None or 'DES', determining encryption of the
			messages sent to the agent 
		authKey -- authorisation key (password) for the agent 
		privKey -- key used to obscure requests from eavesdroppers
		"""
		if authKey is None:
			authProtocol = None 
		if privKey is None:
			privProtocol = None 
		authProtocol = self.AUTH_PROTOCOL_REGISTRY[ authProtocol ]
		privProtocol = self.PRIV_PROTOCOL_REGISTRY[ privProtocol ]
		key = ( authProtocol, authKey, privProtocol, privKey )
		paramName = self._v3paramCache.get( key )
		if paramName is None:
			nameID = self._newV3Name()
			name = 'v3user-%s'%(nameID)
			config.addV3User(
				engine, name, 
				authProtocol=authProtocol, authKey=authKey,
				privProtocol=privProtocol, privKey=privKey
			)
			if authProtocol is config.usmNoAuthProtocol:
				paramType = "noAuthNoPriv"
			elif privProtocol is config.usmNoPrivProtocol:
				paramType = "authNoPriv"
			else:
				paramType = "authPriv"
			paramName = 'v3param-%s'%(nameID)
			config.addTargetParams(
				engine, paramName, name, paramType,
				mpModel = 3
			)
			self._v3paramCache[ key ] = paramName
		return self._targetName( engine, ip, port, paramName )
