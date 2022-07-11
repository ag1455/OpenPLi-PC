from twistedsnmp import bisectoidstore, agent, errors
import unittest
from twistedsnmp.pysnmpproto import v2c,v1, error
try:
	from twistedsnmp import bsdoidstore
except ImportError:
	bsdoidstore = None
if not hasattr( bsdoidstore, 'BSDOIDStore' ):
	# some weird bug is creating the module even though
	# it's failing with an ImportError :(
	bsdoidstore = None

class StorageTest( unittest.TestCase ):
	def createStorage( self, oids ):
		return bisectoidstore.BisectOIDStore(
			OIDs = oids,
		)
	def testExact( self ):
		store = self.createStorage(
			[
				('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
				('.1.3.6.1.2.1.1.2.0', 32),
				('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
				('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
			]
		)
		result = store.getExactOID( '.1.3.6.1.2.1.1.1.0' )
		assert result[0] == '.1.3.6.1.2.1.1.1.0', result
		assert result[1] == 'Hello world!', result
	def testNext( self ):
		store = self.createStorage(
			[
				('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
				('.1.3.6.1.2.1.1.2.0', 32),
				('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
				('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
			]
		)
		result = store.nextOID( '.1.3.6.1.2.1.1.1.0' )
		assert result[0] == '.1.3.6.1.2.1.1.2.0', result
		assert result[1] == 32, result
	def testNextBig( self ):
		store = self.createStorage(
			[
				('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
				('.1.3.6.1.2.12.1.2.0', 32),
				('.1.3.6.1.2.2.1.3.0', v1.IpAddress('127.0.0.1')),
				('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
			]
		)
		result = store.nextOID( '.1.3.6.1.2.2.1.3.0' )
		assert result[0] == '.1.3.6.1.2.12.1.2.0', result
		assert result[1] == 32, result

	def testIter( self ):
		"""Test basic iteration"""
		store = self.createStorage(
			[
				('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
				('.1.3.6.1.2.12.1.2.0', 32),
				('.1.3.6.1.2.2.1.3.0', v1.IpAddress('127.0.0.1')),
				('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
			]
		)
		r = list(iter(store))
		assert len(r) == 4

	def testFromOther( self ):
		"""Test creation of a storage from a sequence of storages"""
		stores = [
			self.createStorage(
				[
					('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
					('.1.3.6.1.2.12.1.2.0', 32),
					('.1.3.6.1.2.2.1.3.0', v1.IpAddress('127.0.0.1')),
					('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
				]
			),
			self.createStorage(
				[
					('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
					('.1.4.6.1.2.12.1.2.0', 32),
					('.1.4.6.1.2.2.1.3.0', v1.IpAddress('127.0.0.1')),
					('.1.4.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
				]
			),
		]
		store = self.createStorage(
			stores
		)
		r = list(iter(store))
		assert len(r) == 7

class RecursiveTest( unittest.TestCase ):
	"""Test Bisect OIDStore with nested storages"""
	def testExact( self ):
		"""Do we get child OIDstore's exact values?"""
		store = bisectoidstore.BisectOIDStore(
			[
				('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
				('.1.3.6.1.2.1.1.2.0', 32),
				('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
			]
		)
		store.setValue(
			'.1.3.6.1.2.1.1.3',
			bisectoidstore.BisectOIDStore(
				[
					('.1.3.6.1.2.1.1.3.%d'%i,i)
					for i in range(32)
				]
			)
		)
		result = store.getExactOID( '.1.3.6.1.2.1.1.3.5' )
		assert result[0] == '.1.3.6.1.2.1.1.3.5', result
		assert result[1] == 5, result
	def testFirst( self ):
		"""Test that firstOID properly chains in/out of sub-storages"""
		store = bisectoidstore.BisectOIDStore(
			[
			]
		)
		store.setValue( 
			'.1.3.6.1.2.1.1.3',
			bisectoidstore.BisectOIDStore(
				[
				]
			)
		)
		self.failUnlessRaises(
			errors.OIDNameError,
			store.firstOID,
		)
		store.setValue(
			'.1.3.6.1.2.1.1.4.0',
			32,
		)
		result = store.firstOID( )
		assert result==('.1.3.6.1.2.1.1.4.0', 32, ), result
		store.getExactOID( '.1.3.6.1.2.1.1.3')[1].setValue(
			'.1.3.6.1.2.1.1.3.0',
			32,
		)
		result = store.firstOID( )
		assert result==('.1.3.6.1.2.1.1.3.0', 32, ), result
	def testSet( self ):
		"""Test that setting a value chains into sub-storages"""
		store = bisectoidstore.BisectOIDStore(
			[
			]
		)
		store.setValue( 
			'.1.3.6.1.2.1.1.3',
			bisectoidstore.BisectOIDStore(
				[
				]
			)
		)
		store.setValue(
			'.1.3.6.1.2.1.1.3.4',
			32,
		)
		subStorage = store.getExactOID( '.1.3.6.1.2.1.1.3')[1]
		assert len(subStorage.OIDs) == 1, (subStorage.OIDs,store.OIDs)
		store.setValue(
			'.1.3.6.1.2.1.1.4.0',
			32,
		)
		assert len(subStorage.OIDs) == 1, (subStorage.OIDs,store.OIDs)
		assert len(store.OIDs) == 2, store.OIDs
		store.setValue(
			'.1.3.6.1.2.1.1.0.0',
			32,
		)
		assert len(subStorage.OIDs) == 1, (subStorage.OIDs,store.OIDs)
		assert len(store.OIDs) == 3, store.OIDs
		store.setValue( 
			'.1.3.6.1.2.1.1.3.5',
			bisectoidstore.BisectOIDStore(
				[
				]
			)
		)
		assert len(subStorage.OIDs) == 2, (subStorage.OIDs,store.OIDs)
		store.setValue( 
			'.1.3.6.1.2.1.1.3.5.3',
			32,
		)
		assert len(subStorage.OIDs) == 2, (subStorage.OIDs,store.OIDs)
		subStorage2 = store.getExactOID( '.1.3.6.1.2.1.1.3.5')[1]
		assert len(subStorage2.OIDs) == 1, (subStorage2.OIDs,subStorage.OIDs)
	def testNext( self ):
		"""Test that getNext properly chains into/out-of sub-storages"""
		store = bisectoidstore.BisectOIDStore(
			[
			]
		)
		self.failUnlessRaises(
			errors.OIDNameError,
			store.nextOID,
			'.1.3.6.1',
		)
		store.setValue( 
			'.1.3.6.1.2.1.1.3',
			bisectoidstore.BisectOIDStore(
				[
				]
			)
		)
		subStorage = store.getExactOID( '.1.3.6.1.2.1.1.3')[1]
		self.failUnlessRaises(
			errors.OIDNameError,
			store.nextOID,
			'.1.3.6.1',
		)
		store.setValue(
			'.1.3.6.1.2.1.1.3.4',
			32,
		)
		result = store.nextOID( '.1.3.6.1' )
		assert result == ( '.1.3.6.1.2.1.1.3.4', 32 ), result
		store.setValue(
			'.1.3.6.1.2.1.1.3.3',
			44,
		)
		result = store.nextOID( '.1.3.6.1' )
		assert result == ( '.1.3.6.1.2.1.1.3.3', 44 ), result
	def testCalculated( self ):
		store = bisectoidstore.BisectOIDStore(
			[
				('.1.3.6.1.2.1.1.1.0', lambda oid,store: 550),
				('.1.3.6.1.2.12.1.2.0', lambda oid,store: 555 ),
				('.1.3.6.1.2.2.1.3.0', v1.IpAddress('127.0.0.1')),
				('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
			]
		)
		result = store.getExactOID( '.1.3.6.1.2.12.1.2.0' )
		assert result[0] == '.1.3.6.1.2.12.1.2.0', result
		assert result[1] == 555, result
		result = store.nextOID( '.1.3.6.1.2.2.1.3.0' )
		assert result[0] == '.1.3.6.1.2.12.1.2.0', result
		assert result[1] == 555, result
		result = store.firstOID(  )
		assert result[0] == '.1.3.6.1.2.1.1.1.0', result
		assert result[1] == 550, result

	
		
if bsdoidstore:
	class BSDTest( object ):
		def createStorage( self, oids ):
			return bsdoidstore.BSDOIDStore(
				bsdoidstore.BSDOIDStore.open( 'temp.bsd', 'n'),
				OIDs = oids,
			)
	class BSDStorageTest( BSDTest, StorageTest ):
		def testRetention( self ):
			"""Test that oids are stored and retrieved properly"""
			store = self.createStorage(
				[
					('.1.3.6.1.2.1.1.1.0', 'Hello world!'),
					('.1.3.6.1.2.1.1.2.0', 32),
					('.1.3.6.1.2.1.1.3.0', v1.IpAddress('127.0.0.1')),
					('.1.3.6.1.2.1.1.4.0', v1.OctetString('From Octet String')),
				]
			)
			store.close()
			newStore = bsdoidstore.BSDOIDStore( 'temp.bsd' )
			result = newStore.getExactOID( '.1.3.6.1.2.1.1.1.0' )
			assert result[0] == '.1.3.6.1.2.1.1.1.0', result
			assert result[1] == 'Hello world!', result
			



if __name__ == "__main__":
	unittest.main()