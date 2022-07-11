"""Mirror a remote agent to a local file"""
from twisted.internet import reactor
from twistedsnmp import snmpprotocol, bsdoidstore, agentproxy

def main( proxy, oidStore, OIDs=('.1.3',) ):
	"""Do a getTable on proxy for OIDs and store in oidStore"""
	oidStore = openStore( oidStore )
	def rowCallback( root, key,value, oidStore = oidStore):
		print key, '-->', repr(value)
		oidStore.setValue( key, value )
	df = proxy.getTable(
		OIDs, retryCount=10,
		recordCallback=rowCallback
	)
	def errorReporter( err ):
		print 'ERROR', err
		raise
	def exiter( value, oidStore=oidStore ):
		reactor.stop()
		print 'closing'
		oidStore.close()
		return value
	df.addCallback( exiter )
	df.addErrback( errorReporter )
	df.addCallback( exiter )
	return df

def openStore( oidStore ):
	oidStore = bsdoidstore.BSDOIDStore(
		bsdoidstore.BSDOIDStore.open( oidStore, mode='n' ),
	)
	return oidStore

##def integrate( results, oidStore ):
##	"""Integrate new results into the oidStore"""
##	for table, records in results.items():
##		for oid,value in records.items():
##			oidStore[ oid ] = value
##	oidStore.btree.sync()
	

if __name__ == "__main__":
	# need to get the ip address
	usage = """Usage:
	mirroragent ipAddress community filename baseoid...

ipAddress -- dotted IP address of the agent
community -- community string for the agent
filename -- filename to use for storing the results
baseoid -- dotted set of OIDs to retrieve from agent
"""
	import sys
	if len(sys.argv) < 4:
		print usage
		sys.exit( 1 )
	ipAddress = sys.argv[1]
	port = reactor.listenUDP(
		20000, snmpprotocol.SNMPProtocol(),
	)
	client = agentproxy.AgentProxy(
		ipAddress, 161,
		community = sys.argv[2],
		snmpVersion = 'v2',
		protocol = port.protocol,
	)
	reactor.callLater( 1, main, client, sys.argv[3], sys.argv[4:] )
	reactor.run()
