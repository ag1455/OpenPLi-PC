"""TwistedSNMP: SNMP Protocol implementation for Twisted Matrix

SNMP defines two major roles for computer systems:

	Agents -- computers which respond to SNMP requests, the
		"server" in a classic client-server model
	Managers -- computers which request information via SNMP,
		the "client" in a classic client-server model

TwistedSNMP provides a primarily manager-side implementation,
with enough agent-side implementation to allow for easy testing
of the manager-side implementation.

There are at least two levels on each side of the implementation:

	protocol -- very low level mechanism for transmitting and
		dispatching messages
	Agent/AgentProxy -- objects providing simple APIs for
		writing applications using SNMP

with the Agent side also having an "OIDStore" layer which
provides for storage and retrieval of ordered OID sets for
querying via the Agent object.

TwistedSNMP is built on top of the PySNMP pure-Python SNMP
package, which provides the message formatting and decoding
operations required for communication.
"""