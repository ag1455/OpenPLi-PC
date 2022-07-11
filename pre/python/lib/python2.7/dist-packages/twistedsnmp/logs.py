"""Logging facilities for TwistedSNMP

We're using standard Python logging because that's what the
application in which TwistedSNMP is used (by it's author)
uses.  This module injects getException as a classmethod
on Logger objects, and makes err a synonym for error.

After that's done, we just define a number of standard logs
to be used throughout the TwistedSNMP empire :) .  Each uses
the prefix 'twsnmp.' for the logging name.

XXX If there's a decent standard logging to twisted logging
bridge, should use that...
"""
import traceback, cStringIO, logging

def getException(error):
	"""Get formatted exception"""
	exception = str(error)
	file = cStringIO.StringIO()
	try:
		traceback.print_exc( limit=10, file = file )
		exception = file.getvalue()
	finally:
		file.close()
	return exception

logging.Logger.getException = staticmethod( getException )
logging.Logger.err = logging.Logger.error
logging.Logger.DEBUG = logging.DEBUG 
logging.Logger.WARN = logging.WARN 
logging.Logger.INFO = logging.INFO 
logging.Logger.ERROR = logging.Logger.ERR = logging.ERROR

# now the actual logs...
protocol_log = logging.getLogger( 'twsnmp.protocol' )
agentprotocol_log = logging.getLogger( 'twsnmp.agentprotocol' )
tableretriever_log = logging.getLogger( 'twsnmp.table' )
agentproxy_log = logging.getLogger( 'twsnmp.agentproxy' )
massretriever_log = logging.getLogger( 'twsnmp.massretriever' )

#protocol_log.setLevel( logging.DEBUG )
#agentprotocol_log.setLevel( logging.DEBUG )
try:
	logging.basicConfig()
except Exception, err:
	pass
