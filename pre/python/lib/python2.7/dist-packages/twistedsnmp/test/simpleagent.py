"""Simplistic agent to allow for interactive testing"""
from twistedsnmp import agentprotocol, agent, bisectoidstore
from twistedsnmp.pysnmpproto import v2c,v1, error, oid
from twisted.internet import error as twisted_error
from twisted.internet import reactor
import logging

logging.basicConfig()
logging.getLogger("twsnmp.agentprotocol").setLevel( logging.DEBUG )

def main( ):
	ports = [161]+range(20000,25000)
	for port in ports:
		try:
			reactor.listenUDP(
				port, agentprotocol.AgentProtocol(
					snmpVersion = 'v2c',
					agent = agent.Agent(
						dataStore = createStorage(),
					),
				),
			)
			print 'listening on port', port
			return port
		except twisted_error.CannotListenError:
			pass
			
def createStorage( oidsForTesting = [
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
]):
		return bisectoidstore.BisectOIDStore(
			OIDs = oidsForTesting,
		)
	
			
			
if __name__ == "__main__":
	reactor.callWhenRunning( main )
	reactor.run()
