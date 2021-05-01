"""Tests for SNMP trap sending/receiving"""
from twistedsnmp.test import basetestcase
from twistedsnmp.pysnmpproto import v1, oid, alpha
from twistedsnmp import agent
from twisted.internet import defer, reactor
import unittest

class TrapTestsV1( basetestcase.BaseTestCase ):
	version = 'v1'
	oidsForTesting = [
		('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
		('.1.3.6.1.2.1.1.2.0', 32),
		('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
		('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
	]
	def test_simpleTrap( self ):
		"""Is a trap handled by a completely generic trap handler registration?"""
		self.client.listenTrap(
			callback = self.storeTrap,
		)
		theAgent = self.agent.protocol.agent
		handler = agent.TrapHandler(
			managerIP = ('127.0.0.1',self.client.protocol.transport.port),
		)
		theAgent.registerTrap( handler )
		theAgent.sendTrap( pdus=[
			('.1.3.6.1.2.1.1.3.0',None),
		])
		self.runFor( 1 )
		# now, should receive it over on the client...
		assert self.trap
		
	def test_exactTrap( self ):
		"""Is a trap handled by a completely generic trap handler registration?"""
		self.client.listenTrap(
			genericType=6, specificType=8,
			callback = self.storeTrap,
		)
		print self.client.protocol._trapRegistry
		theAgent = self.agent.protocol.agent
		handler = agent.TrapHandler(
			managerIP = ('127.0.0.1',self.client.protocol.transport.port),
			genericType = None,
			specificType = None,
		)
		theAgent.registerTrap( handler )
##		import pdb
##		pdb.set_trace()
		theAgent.sendTrap( 
			genericType = 6, specificType = 8,
			pdus=[
				('.1.3.6.1.2.1.1.3.0',None),
			]
		)
		self.runFor( 1 )
		# now, should receive it over on the client...
		assert self.trap
		del self.trap
		theAgent.sendTrap( 
			# specificType does not match, so should not be processed
			genericType = 6, specificType = 0,
			pdus=[
				('.1.3.6.1.2.1.1.3.0',None),
			]
		)
		self.runFor( 1 )
		assert not getattr( self, 'trap', None )

	def runFor( self, seconds=1 ):
		df = defer.Deferred()
		def finish( ):
			df.callback( None )
		reactor.callLater( seconds, finish )
		self.doUntilFinish( df )
	def storeTrap( self, trap, address ):
		self.trap = trap 
		self.trapAddress = address
		printTrap( trap )
		return trap

def printTrap( req ):
	pdu = req.apiAlphaGetPdu()
	if req.apiAlphaGetProtoVersionId() == alpha.protoVersionId1:
		print 'Enterprise: %s\n' % pdu.apiAlphaGetEnterprise() + \
			  'Agent Address: %s\n' % pdu.apiAlphaGetAgentAddr() + \
			  'Generic Trap: %s\n' % pdu.apiAlphaGetGenericTrap() + \
			  'Specific Trap: %s\n' % pdu.apiAlphaGetSpecificTrap() + \
			  'Uptime: %s\n' % pdu.apiAlphaGetTimeStamp() + \
			  'Var-binds:'
	for varBind in pdu.apiAlphaGetVarBindList():
		print varBind.apiAlphaGetOidVal()


class TrapTestsV2c( TrapTestsV1 ):
	version = 'v2c'

##if basetestcase.bsdoidstore:
##	class SetRetrieverV1BSD( basetestcase.BSDBase, SetRetrieverV1 ):
##		pass
##	class SetRetrieverV2CBSD( basetestcase.BSDBase, SetRetrieverV2C ):
##		pass
##
if __name__ == "__main__":
	unittest.main()
	
