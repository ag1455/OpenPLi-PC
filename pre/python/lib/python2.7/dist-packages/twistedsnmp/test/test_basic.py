from __future__ import nested_scopes
from twisted.internet import reactor
import unittest
from twistedsnmp.test import basetestcase
from twistedsnmp import tableretriever, agentproxy
from twistedsnmp.pysnmpproto import v2c,v1, error

class BasicProxyTests( basetestcase.BaseTestCase ):
	version = 'v2c'
	def testBulkRequestCreate( self ):
		"""Test that we can create bulk requests"""
		request = self.client.encode(
			[
				'.1.3.6.2.3.4.5.6',
			],
			self.client.community,
			next= True,
			bulk = True,
			maxRepetitions = 256,
		)
		request.encode()
		r1ID = request.apiGenGetPdu()['request_id'].get()
		rkey1 = self.client.getRequestKey( request )
		request2 = self.client.encode(
			[
				'.1.3.6.2.3.4.5.6',
			],
			self.client.community,
			next= True,
			bulk = True,
			maxRepetitions = 256,
		)
		assert request2 is request, (request,request2)
		r2ID = request.apiGenGetPdu()['request_id'].get()
		rkey2 = self.client.getRequestKey( request )
		assert r2ID != r1ID, (r2ID,r1ID)
		assert rkey1 != rkey2, (rkey1,rkey2)
	def testRequestOIDCache( self ):
		anOID = '.1.3.6.2.3.4.5.6.10000.10000.10000'
		if hasattr( self.client, 'cacheOIDEncoding' ):
			self.client.cacheOIDEncoding( anOID )
		request = self.client.encode(
			[
				anOID,
			],
			self.client.community,
			next= True,
			bulk = True,
			maxRepetitions = 256,
		)
		message = request.encode()
		newMessage = self.client.implementation.Request()
		newMessage.decode( message )
		pdu = newMessage.apiGenGetPdu()
		variables = pdu.apiGenGetVarBind()


class TableRetrieverTests( basetestcase.BaseTestCase ):
	version = 'v2c'
	def testCreation( self ):
		self.installMessageCounter()
		tr = tableretriever.TableRetriever(
			self.client,
			['.1.3.6'],
		)
	



if __name__ == "__main__":
	unittest.main()
	
