"""SNMP Protocol for Twisted

This protocol exposes most of the functionality of the pysnmp
manager side operations, with the notable exceptions of traps,
and retrieval from large numbers of agents.

Parallel retrieval from large numbers of agents should be
doable simply by creating ports for each agent and calling
get on that port's protocol.
"""
from twisted.internet import protocol, reactor
from twisted.internet import error as twisted_error
from twistedsnmp.pysnmpproto import v2c,v1, error, alpha
import traceback
from twistedsnmp import datatypes, agentproxy
from twistedsnmp.logs import protocol_log as log

class SNMPProtocol(protocol.DatagramProtocol):
	"""Base class for SNMP datagram protocol

	attributes:
		requests -- dictionary holding request-key: df,timer
			where request-keys are calculated by our getRequestKey
			method, df is the defer for callbacks to the request,
			and timer is the timeout timer for the request.
	"""
	def __init__(self, port=20000 ):
		"""Initialize the SNMPProtocol object

		port -- port on which we are listening...
		"""
		self.port = port
		self.requests = {}
		
	# Twisted entry points...
	def datagramReceived(self, datagram, address):
		"""Process a newly received datagram

		Converts the message to a pysnmp response
		object, then dispatches it to the appropriate
		callback based on the message ID as determined
		by self.getRequestKey( response, address ).

		Passes on the response object itself to the
		callback, as the response object is needed for
		table download and the like.
		"""
		response = self.decode(datagram)
		if response is None:
			log.warn(
				"""Bad response from %r: %r""",
				address, datagram,
			)
			return
		try:
			key = self.getRequestKey( response, address )
		except KeyError, err:
			key = None
		if key in self.requests:
			df,timer = self.requests[key]
			if hasattr( timer, 'cancel' ):
				try:
					timer.cancel()
				except (twisted_error.AlreadyCalled,twisted_error.AlreadyCancelled):
					pass
			del self.requests[key]
			try:
				df.callback( response )
			except (twisted_error.AlreadyCalled,twisted_error.AlreadyCancelled):
				pass
		elif self.handleTrap( response, address ):
			pass
		else:
			# is a timed-out response that finally arrived
			log.info(
				"""Unexpected request key %r, %r requests pending %s""",
				key,
				len(self.requests),
				repr(self.requests.keys())[:100],
			)
	def handleTrap( self, request, address ):
		"""Handle a trap message from an agent"""
		log.debug( 'handleTrap: %s', request )
		traps = getattr( self, '_trapRegistry', None )
		if not traps:
			return False
		if traps.has_key( address ):
			generics = traps[address]
		elif traps.has_key( None ):
			generics = traps[ None ]
		else:
			return False
		# okay, now see what we're listening to for this agent...
		# XXX is v1-specific at the moment...
		if not generics:
			return False 
		try:
			pdu = request.apiAlphaGetPdu()
			if request.apiAlphaGetProtoVersionId() == alpha.protoVersionId1:
				genericType = pdu.apiAlphaGetGenericTrap()
				specificType = pdu.apiAlphaGetSpecificTrap()
				community = request.apiAlphaGetCommunity()
			else:
				return False
			found = False
			for genericKey in (genericType,None):
				specifics = generics.get(genericKey)
				if specifics:
					for specificKey in (specificType,None):
						callbacks = specifics.get( specificKey )
						if callbacks:
							for callbackKey in (community,None):
								callback = callbacks.get( callbackKey )
								if callable( callback ):
									callback( request, address )
									found = True
			return found
		except Exception, err:
			log.warn(
				"""Failure processing trap %s from %s: %s""",
				address,
				request,
				log.getException( err ),
			)
		return False
	def send(self, request, target):
		"""Send a request (string) to the network"""
		return self.transport.write( request, target )
		
	# implementation details...
	def getRequestKey( self, request, target ):
		"""Get the request key from a request/response"""
		for key in [
			'get_request', 'get_response',
			'get_next_request', 'get_bulk_request',
			'response', 'set_request',
		]:
			try:
				ID = request['pdu'][key]['request_id']
			except KeyError, err:
				pass
			except TypeError, err:
				log.error(
					"""Unexpected TypeError retrieving request key %r: %s""",
					key, log.getException(err),
				)
			else:
				return target, ID.get()
		raise KeyError( """Unable to get a request key id from %s for target %s"""%( request, target))

	def decode( self, message ):
		"""Decode a datagram message"""
		for implementation in v2c, v1:
			try:
				response = implementation.GetResponse()
				response.decode( message )
				return response
			except Exception, err:
				pass
		try:
			metaReq = alpha.MetaMessage()
			metaReq.decode( message )
			return metaReq.apiAlphaGetCurrentComponent()
		except Exception, err:
			pass
		return None

def port( portNumber=-1, protocolClass=SNMPProtocol ):
	"""Create a new listening TwistedSNMP port (with attached protocol)

	portNumber -- a numeric port specifier, or a sequence of
		numeric port specifiers to search
		if not specified, defaults to range(25000,30000)
	protocolClass -- the protocol class to create, will
		be called with default arguments () to create the
		protocol instance
		
		XXX should that be an instance? this is a convenience
		method, but seems silly to restrict it to protocols
		that have the same initialiser.  Oh well.

	This is a convenience function which allows you to specify
	a range of UDP ports which will be searched in order to
	create a new TwistedSNMP protocol.  Since the client-side
	protocol's port number is of minimal interest it is often
	handy to have this functionality available.

	returns Twisted UDP port object, with the SNMPProtocol
		instance available as port.protocol on that object
	"""
	if portNumber == -1:
		ports = xrange(25000,30000)
	elif isinstance( portNumber, (int,long)):
		ports = [portNumber]
	else:
		ports = portNumber
	for port in ports:
		try:
			return reactor.listenUDP(
				port, protocolClass(),
			)
		except twisted_error.CannotListenError:
			pass
	raise twisted_error.CannotListenError(
		'localhost', port, 
		"""Could not listen on *any* port in our range of potential ports! %s"""%(
			repr(ports)[:30],
		),
	)

def test():
	port = reactor.listenUDP(20000, SNMPProtocol() )
	proxy = agentproxy.AgentProxy(
		"205.207.149.252", 161, protocol = port.protocol,
	)
	def onSuccess( value ):
		print 'Success:'
		if isinstance( value, dict ):
			value = value.items()
		for key,item in value:
			print key, len(item)
	def onFailure( reason ):
		print 'Failure:', reason
	d = proxy.get( ['.1.3.6.1.2.1.1.1.0', '.1.3.6.1.2.1.1.5.0', '.1.3.6.1.2.1.1.6.0'] )
	d.addCallbacks( onSuccess, onFailure )

	d = proxy.getTable( [ '.1.3.6.1.4.1.1456.2.2.6.1.3' ] )
	d.addCallbacks( onSuccess, onFailure )

	proxy2 = agentproxy.AgentProxy(
		"205.207.149.252",
		community = 'public',
		snmpVersion = 'v2',
		protocol = port.protocol,
	)
	d = proxy2.getTable( [
		'.1.3.6.1.4.1.1456.2.2.6.1.2',
		'.1.3.6.1.4.1.1456.2.3.2.1.18',
	] )
	d.addCallbacks( onSuccess, onFailure )
	
	

def main():
	reactor.callLater( 1, test)
	reactor.run()

if __name__ == "__main__":
	main()
