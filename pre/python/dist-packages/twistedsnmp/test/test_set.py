from twistedsnmp.test import basetestcase
from twistedsnmp.pysnmpproto import v1, oid
import unittest

class SetRetrieverV1( basetestcase.BaseTestCase ):
	version = 'v1'
	oidsForTesting = [
		('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
		('.1.3.6.1.2.1.1.2.0', 32),
		('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
		('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
	]
	def test_setEndOfOIDs( self ):
		"""After a set, is the set value retrieved?"""
		d = self.client.set(
			[('.1.3.6.1.2.1.1.5.0',3)],
		)
		self.doUntilFinish( d )
		d = self.client.get(
			['.1.3.6.1.2.1.1.5.0',],
		)
		self.doUntilFinish( d )
		assert self.success, self.response
##		import pdb
##		pdb.set_trace()
		assert self.response == { oid.OID('.1.3.6.1.2.1.1.5.0'):3 }, self.response

	def test_setReplaceAnOID( self ):
		"""After a replace-set, is the set value retrieved?"""
		d = self.client.set(
			[('.1.3.6.1.2.1.1.4.0',3)],
		)
		self.doUntilFinish( d )
		d = self.client.get(
			['.1.3.6.1.2.1.1.4.0',],
		)
		self.doUntilFinish( d )
		assert self.success, self.response
		assert self.response == { oid.OID('.1.3.6.1.2.1.1.4.0'):3 }
	def test_socketFailure( self ):
		"""Test for failure due to sending-time socket failure"""
		import socket
		def mockSend( message ):
			raise socket.error(65, 'No route to host')
		self.client.send = mockSend
		d = self.client.set(
			[('.1.3.6.1.2.1.1.4.0',3)],
		)
		self.doUntilFinish( d )
		assert not self.success
		assert isinstance( self.response.value, socket.error )
		assert self.response.value.args == (65,'No route to host')
		
class SetRetrieverV2C( SetRetrieverV1 ):
	version = 'v2c'

if basetestcase.bsdoidstore:
	class SetRetrieverV1BSD( basetestcase.BSDBase, SetRetrieverV1 ):
		pass
	class SetRetrieverV2CBSD( basetestcase.BSDBase, SetRetrieverV2C ):
		pass

if __name__ == "__main__":
	unittest.main()
	