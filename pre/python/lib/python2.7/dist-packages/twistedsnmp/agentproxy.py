"""Client/manager side object for querying Agent via SNMPProtocol"""
from twistedsnmp import pysnmpproto
if pysnmpproto.pysnmpversion == 4:
	from twistedsnmp.v4.agentproxy import *
else:
	from twistedsnmp.v3.agentproxy import *
