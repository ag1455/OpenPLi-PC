"""Protocol implementation for Agent/Manager-side API"""
from twisted.internet import defer, protocol, reactor
from twistedsnmp.pysnmpproto import v2c,v1, error
from pysnmp import error as pysnmp_error
from pysnmp.asn1 import error as asnerror
from twistedsnmp.logs import agentprotocol_log as log
#log.setLevel( log.WARN )

class AgentProtocol(protocol.ConnectedDatagramProtocol):
	"""Base class for SNMP datagram protocol

	The AgentProtocol object is responsible for handling
	incoming datagrams (strings) and converting them to
	PySNMP message objects.  It is also responsible for
	sending messages from the Agent back across the network.

	In addition it provides a few utility methods.
	"""
	agent = None
	def __init__(
		self, interface=None, port=161, community='public',
		snmpVersion = 'v2', agent=None,
	):
		"""Initialize the SNMPProtocol object

		interface -- interface (IP) on which to bind
		port -- port for the connection
		community -- community to use for SNMP conversations
		snmpVersion -- '1' or '2', indicating the supported version,
			normally you would want a real-world Agent to use the
			highest available version (v2c, at the moment), but for
			testing purposes it is occasionally useful to set the
			version to v1.
		"""
		self.interface = interface
		self.port = port
		self.community = community
		self.snmpVersion = snmpVersion
		if self.snmpVersion in ("2",'2c','v2','v2c', v2c):
			self.implementations = [v2c,v1]
		else:
			self.implementations = [v1]
		if agent is not None:
			self.setAgent( agent )
			agent.setProtocol( self )
	def setAgent( self, agent ):
		"""Set the agent implementation for this protocol"""
		self.agent = agent
	# Twisted entry points...
	def datagramReceived(self, datagram, address):
		"""Process a newly received datagram

		Converts the message to a pysnmp request
		object, then dispatches it to the appropriate
		handler(s) based on the requested OIDs, collects
		the results and returns them in a response object

		XXX Needs to do minimal authentication at least!
		"""
		log.debug( 'datagram in from %s: %r', address, datagram )
		processed = 0
		for implementation in self.implementations:
			request = implementation.Request()
			try:
				request.decode(datagram)
				processed = 1
			except asnerror.ValueConstraintError, err:
				pass
			except pysnmp_error.PySnmpError, why:
				log.error( 'Malformed inbound message dropped: %s', why )
				continue
			else:
				if self.verifyIdentity( request, address ):
					# Fetch Object ID's and associated values
					vars = request.apiGenGetPdu().apiGenGetVarBind()
					agent = self.agent
					if agent is None:
						# close down the protocol, as the agent is gone?
						return
					requestType = self.requestType( request )
					if requestType == 'get_request':
						agent.get( request, address, implementation )
					elif requestType == 'get_next_request':
						agent.getNext( request, address, implementation )
					elif requestType == 'get_bulk_request':
						agent.getTable( request, address, implementation )
					elif requestType == 'set_request':
						agent.set( request, address, implementation )
					else:
						log.error( "Unrecognised request type %r", requestType )
				break
		if not processed:
			log.warn(
				'Warning: unable to decode message from %s:  %s',
				address, datagram,
			)
	def requestType( self, request ):
		"""Retrieve the request-type from the request"""
		return request['pdu'].keys()[0]
	def send(self, response, address):
		"""Send a request (string) to the network"""
		self.transport.write(response, address)
	def verifyIdentity( self, request, address ):
		"""Verify that the address and message-community are valid

		XXX I believe v3 has proper authentication available.

		XXX This *should* be part of the Agent class!
		"""
		if self.community is not None and request.apiGenGetCommunity() != self.community:
			# SNMP agents generally just ignore messages with invalid comm strings
			return 0
		return 1
