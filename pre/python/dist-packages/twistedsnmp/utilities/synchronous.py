from twisted.internet import reactor, defer

__metaclass__ = type

class DoUntilFinished:
	success = 0
	finished = 0
	timeout = 0
	result = None
	def __init__( self, *defers ):
		"""Initialise the DoUntilFinished instance

		defers -- Defer objects to be handled
		"""
		if not defers:
			raise ValueError( """Need at least one Defer for DoUntilFinished""" )
		elif len(defers) == 1:
			myDefer = defers[0]
		else:
			myDefer = defer.DeferList(
				defers
			)
		self.defer = myDefer
	def __call__( self, timeout=None ):
		self.defer.addCallbacks( self.OnSuccess, self.OnFailure )
		if timeout:
			reactor.callLater( timeout, self.OnTimeout )
		reactor.run()
	def OnTimeout( self ):
		"""On a timeout condition, raise an error"""
		if not self.finished:
			self.finished = 1
			self.result = defer.TimeoutError('SNMP request timed out')
			self.success = 0
		reactor.crash()
	def OnSuccess( self, result ):
		if not self.finished:
			self.finished = 1
			self.result = result
			self.success = 1
		reactor.crash()
	def OnFailure( self, errorMessage ):
		if not self.finished:
			self.finished = 1
			self.result = errorMessage
			self.success = 0
		reactor.crash()

def doUntil( *defers ):
	"""Run a set of defers until complete"""
	d = DoUntilFinished( *defers )
	d( )
	if not d.success:
		raise d.result.value
	else:
		return d.result


def synchronous( timeout, callable, *arguments, **named ):
	"""Call callable in twisted

	timeout -- timeout in seconds, specify 0 or None to disable
	callable -- defer-returning callable object
	arguments, named -- passed to callable within reactor

	returns (success, result/error)
	"""
	df = callable( *arguments, **named )
	return doUntil( df )

if __name__ == "__main__":
	import sys
	if not sys.argv[1:]:
		print """For testing run:
	synchronous server
or
	synchronous client
from the command line."""
		sys.exit( 1 )
		
	if sys.argv[1] == 'server':
		# just setup something to serve a response
		from twistedsnmp import agent, agentprotocol, bisectoidstore
		from twistedsnmp.pysnmpproto import v2c,v1, error
		agentObject = reactor.listenUDP(
			20161, agentprotocol.AgentProtocol(
				snmpVersion = 'v1',
				agent = agent.Agent(
					dataStore = bisectoidstore.BisectOIDStore(
						OIDs = [
							('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
							('.1.3.6.1.2.1.1.2.0', 32),
							('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
							('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
							('.1.3.6.1.2.1.2.1.0', 'Hello world!'),
							('.1.3.6.1.2.1.2.2.0', 32),
							('.1.3.6.1.2.1.2.3.0', v1.IpAddress('127.0.0.1')),
							('.1.3.6.1.2.1.2.4.0', v1.OctetString('From Octet String')),
							('.1.3.6.2.1.0', 'Hello world!'),
							('.1.3.6.2.2.0', 32),
							('.1.3.6.2.3.0', v1.IpAddress('127.0.0.1')),
							('.1.3.6.2.4.0', v1.OctetString('From Octet String')),
						]
					),
				),
			),
		)
		print 'Starting listening agent'
		reactor.run()
	else:
		from twistedsnmp import agentproxy, snmpprotocol
		port = snmpprotocol.port()
		proxy = agentproxy.AgentProxy(
			ip = '127.0.0.1',
			community = 'public',
			protocol = port.protocol,
			port = 20161,
		)
		proxy.verbose = 1
		print synchronous( 0, proxy.getTable, ('.1.3.6.1.2.1.1',) )
		