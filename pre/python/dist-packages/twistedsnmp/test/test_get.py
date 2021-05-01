from __future__ import nested_scopes
from twisted.internet import reactor
import socket, unittest
from twistedsnmp import agent, agentprotocol, twinetables, agentproxy
from twistedsnmp import snmpprotocol, massretriever, tableretriever
from twistedsnmp.test import basetestcase
from twistedsnmp.pysnmpproto import v2c,v1, error, oid

class GetRetrieverV1( basetestcase.BaseTestCase ):
	version = 'v1'
	oidsForTesting = [
		(oid.OID(key),value)
		for key,value in [
			('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
			('.1.3.6.1.2.1.1.2.0', 32),
			('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
			('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
			('.1.3.6.1.2.1.2.1.0', 'Hello world!'),
			('.1.3.6.1.2.1.2.2.0', 32),
			('.1.3.6.1.2.1.2.3.0', v1.IpAddress('127.0.0.1')),
			('.1.3.6.1.2.1.2.4.0', v1.OctetString('From Octet String')),
		] + [
			('.1.3.6.1.2.1.3.%s.0'%i, 32)
			for i in xrange( 512 )
		] + [
			('.1.3.6.2.1.0', 'Hello world!'),
			('.1.3.6.2.2.0', 32),
			('.1.3.6.2.3.0', v1.IpAddress('127.0.0.1')),
			('.1.3.6.2.4.0', v1.OctetString('From Octet String')),
		]
	]
	#good
	def test_simpleGet( self ):
		"""Can retrieve a single simple value?"""
		d = self.client.get( [
			'.1.3.6.1.2.1.1.1.0',
		] )
		self.doUntilFinish( d )

		assert self.success, self.response
		assert isinstance( self.response, dict ), self.response
		assert self.response.has_key( oid.OID('.1.3.6.1.2.1.1.1.0') ), self.response
		assert self.response[oid.OID('.1.3.6.1.2.1.1.1.0') ] == 'Hello world!', self.response

	#good
	def test_tableGet( self ):
		"""Can retrieve a tabular value?"""
		d = self.client.getTable( [
			'.1.3.6.1.2.1.1'
		] )
		self.doUntilFinish( d )

		assert self.success, self.response
		assert isinstance( self.response, dict ), self.response
		assert self.response.has_key(
			oid.OID('.1.3.6.1.2.1.1')
		), (self.response,self)
		tableData = self.response[oid.OID('.1.3.6.1.2.1.1') ]
		assert isinstance(tableData, dict)
		assert tableData.has_key(oid.OID('.1.3.6.1.2.1.1.1.0')), tableData
	def test_tableGetWithStart( self ):
		"""Can retrieve a tabular value?"""
		d = self.client.getTable( 
			[
				'.1.3.6.1.2.1.1'
			],
			startOIDs = [
				'.1.3.6.1.2.1.1.3.0'
			],
		)
		self.doUntilFinish( d )

		assert self.success, self.response
		assert isinstance( self.response, dict ), self.response
		assert self.response.has_key(
			oid.OID('.1.3.6.1.2.1.1')
		), (self.response,self)
		tableData = self.response[oid.OID('.1.3.6.1.2.1.1') ]
		assert isinstance(tableData, dict)
		# won't have this key because started later...
		assert not tableData.has_key(oid.OID('.1.3.6.1.2.1.1.1.0')), tableData
		# should (only) have this key because started at 3...
		assert tableData.has_key(oid.OID('.1.3.6.1.2.1.1.4.0')), tableData
		assert len(tableData) == 1

	#good
	def test_tableGetMissing( self ):
		"""Does tabular retrieval ignore non-existent oid-sets?"""
		d = self.client.getTable( [
			'.1.3.6.1.2.1.5'
		] )
		self.doUntilFinish( d )
		assert self.success, self.response
		assert self.response == {}, self.response

	#good
	def test_tableGetAll( self ):
		"""Does tabular retrieval work specifying a distant parent (e.g. .1.3.6)?"""
		d = self.client.getTable( [
			'.1.3.6'
		] )
		self.doUntilFinish( d )
		assert self.success, self.response
		assert self.response == {
			oid.OID('.1.3.6'):dict( self.oidsForTesting )
		}, self.response
	#bad
	def test_multiTableGet( self ):
		oids = [
			'.1.3.6.1.2.1.1',
			'.1.3.6.1.2.1.2',
			'.1.3.6.2',
		]
		d = self.client.getTable( oids )
		self.doUntilFinish( d )
		if not self.success:
			raise self.response.value
		else:
			for oidObject in oids:
				assert self.response.has_key( oid.OID(oidObject) )
	#good
	def test_multiTableGetBad( self ):
		oids = [
			'.1.3.6.1.2.1.1',
			'.1.3.6.1.2.1.2',
			'.1.3.6.2',
			'.1.3.6.3',
		]
		d = self.client.getTable( oids )
		self.doUntilFinish( d )
		for oidObject in oids[:-1]:
			assert self.response.has_key( oid.OID(oidObject) )
		assert not self.response.has_key( oid.OID(oids[-1]) ), self.response
	#good
	def test_tableGetErrorReported( self ):
		oids = [
			'.1.3.6.1.2.1.1',
			'.1.3.6.1.2.1.2',
			'.1.3.6.2',
			'.1.3.6.3',
		]
		originalAreWeDone = tableretriever.TableRetriever.areWeDone
		def raiseError( *args, **named ):
			raise TypeError( """Blah""" )
		tableretriever.TableRetriever.areWeDone = raiseError
		try:
			d = self.client.getTable( oids )
			self.doUntilFinish( d )
		finally:
			tableretriever.TableRetriever.areWeDone = originalAreWeDone
		assert not self.success
		assert isinstance( self.response.value, TypeError )
		assert self.response.value.args == ('Blah',)

	#good
	def test_socketFailure( self ):
		"""Test whether socket failure on send is caught properly

		Previous versions have not caught failure-on-send conditions,
		which can wind up having unexpected consequences, particularly
		with things such as mass-retriever, which build on top of the
		basic AgentProxy.
		"""
		import socket
		def mockSend( message ):
			raise socket.error(65, 'No route to host')
		self.client.send = mockSend
		d = self.client.get( [
			'.1.3.6.1.2.1.1.1.0',
		] )
		self.doUntilFinish( d )
		assert not self.success
		assert isinstance( self.response.value, socket.error )
		assert self.response.value.args == (65,'No route to host')

	#good
	def test_socketFailureTable( self ):
		"""Test whether socket failure on send is caught properly for tables

		Previous versions have not caught failure-on-send conditions,
		which can wind up having unexpected consequences, particularly
		with things such as mass-retriever, which build on top of the
		basic AgentProxy.
		"""
		self.client.send = socketErrorSend
		d = self.client.getTable( [
			'.1.3.6.1.2.1.1.1.0',
		], retryCount=2 )
		self.doUntilFinish( d )
		assert not self.success
		assert isinstance( self.response.value, socket.error )
		assert self.response.value.args == (65,'No route to host')
##	def test( self ):
##		pass

def socketErrorSend( message ):
	raise socket.error(65, 'No route to host')

class GetRetrieverV2C( GetRetrieverV1 ):
	version = 'v2c'
	def test_tableGetAllBulk( self ):
		"""Does tabular retrieval do only a single query?"""
		self.installMessageCounter()
		d = self.client.getTable( [
			'.1.3.6'
		] )
		self.doUntilFinish( d )
		assert self.success, self.response
		expected = (len(self.oidsForTesting)/ agentproxy.DEFAULT_BULK_REPETITION_SIZE)+1
		assert self.client.messageCount <= expected, """Took %s messages to retrieve with bulk table, should take less than %r"""%( self.client.messageCount , expected)
	def test_tableGetAllMaxSize( self ):
		"""Does tabular retrieval respect passed maxSize?"""
		def send(request, client= self.client):
			"""Send a request (string) to the network"""
			client.messageCount += 1
			client.protocol.send(request, (client.ip,client.port))
		self.client.messageCount = 0
		self.client.send = send
		d = self.client.getTable( [
			'.1.3.6'
		], maxRepetitions=16 )
		self.doUntilFinish( d )
		assert self.success, self.response
		expected = (len(self.oidsForTesting)/ 16)-1
		assert self.client.messageCount > expected, """Took %s messages to retrieve with bulk table, should take more than %r with maxRepetitions = 16"""%( self.client.messageCount , expected)

if basetestcase.bsdoidstore:
	class GetRetrieverV1BSD( basetestcase.BSDBase, GetRetrieverV1 ):
		pass
	class GetRetrieverV2CBSD( basetestcase.BSDBase, GetRetrieverV2C ):
		pass

class MassRetrieverTest( basetestcase.BaseTestCase ):
	"""Test for mass retrieval of values"""
	version = 'v2'
	oidsForTesting = [
		('.1.3.6.1.1.3',       'Blah!'),
		('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
		('.1.3.6.1.2.1.1.2.0', 32),
		('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
		('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
	]
	def testMassRetriever( self ):
		"""Can we retrieve mass value single-oid values?"""
		proxies = massretriever.proxies(
			self.client.protocol,
			[('127.0.0.1',self.agent.port, 'public',self.version)]*250
		)
		retriever = massretriever.MassRetriever(
			proxies
		)
		retriever.verbose = 1
		d = retriever( oids = ['.1.3.6.1.1.3',] )
		self.doUntilFinish( d )
		assert self.success, self.response
		assert self.response == {
			('127.0.0.1',self.agent.port):
			{oid.OID('.1.3.6.1.1.3'):'Blah!'}
		}, self.response
		retriever.printStats()
	def testMassRetrieverTables( self ):
		"""Can we retrieve mass value tabular sets?"""
		import random
		GOOD_COUNT = 500
		BAD_COUNT = 500
		proxies = massretriever.proxies(
			self.client.protocol,
			[
				('127.0.0.1',self.agent.port, 'public',self.version)
			]* GOOD_COUNT + [
				('127.0.0.1',self.agent.port+10000, 'public',self.version)
			] * BAD_COUNT
		)
		random.shuffle( proxies )
		random.shuffle( proxies )
		random.shuffle( proxies )
		retriever = massretriever.MassRetriever(
			proxies
		)
		retriever.verbose = 1
		d = retriever(
			tables = ['.1.3.6.1.2.1',]
		)
		self.doUntilFinish( d )
		assert self.success, self.response
		expected = {
			('127.0.0.1', self.agent.port): {
				oid.OID('.1.3.6.1.2.1'):{
					oid.OID('.1.3.6.1.2.1.1.1.0'): 'Hello world!',
					oid.OID('.1.3.6.1.2.1.1.2.0'): 32,
					oid.OID('.1.3.6.1.2.1.1.3.0'): '127.0.0.1',
					oid.OID('.1.3.6.1.2.1.1.4.0'): 'From Octet String',
				}
			},
			('127.0.0.1', self.agent.port+10000): {
				oid.OID('.1.3.6.1.2.1'):None,
			},
		}
		assert self.response == expected, (expected,self.response)
		retriever.printStats()
		assert retriever.successCount == GOOD_COUNT, """Expected %s valid responses, got %s"""%(GOOD_COUNT, retriever.successCount )
		assert retriever.errorCount == BAD_COUNT, """Expected %s valid responses, got %s"""%(GOOD_COUNT, retriever.successCount )

class LargeTableTest( basetestcase.BaseTestCase ):
	"""Test for full retrieval of a large table"""
	version = 'v2'
	oidsForTesting = [
		('.1.3.6.1.2.1.1.%s'%i, 32)
		for i in range(1024)
	] + [
		('.1.3.6.1.2.1.2.4', v1.OctetString('From Octet String')),
	]
	def testLargeTable( self ):
		"""Do we retrieve all records for a large table?"""
		d = self.client.getTable( [
			'.1.3.6.1.2.1.1'
		] )
		self.doUntilFinish( d )
		assert self.success, """Failed to retrieve"""
		perRecord = twinetables.twineTables( self.response, self.response.keys())
		assert len(perRecord) == 1024, """Didn't get 1024 records, got %r"""%(len(perRecord))
		
class LargeTableTestv2c( LargeTableTest ):
	"""Test for full retrieval of a large table"""
	version = 'v1'

if __name__ == "__main__":
	unittest.main()
		
