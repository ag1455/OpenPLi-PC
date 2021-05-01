import unittest
import oid

class BasicTests( unittest.TestCase ):
	def test_string( self ):
		"""Can we coerce properly from a string?"""
		for source,expected in [
			(
				'.1.2.3.4.5',
				oid.OID.fromNumeric( (1,2,3,4,5)),
			),
			(
				'.1.somewhere(2).3.this(4).5',
				oid.OID.fromNumeric( (1,2,3,4,5)),
			),
			(
				'...1.  somewhere(2). \n3.this(4).5',
				oid.OID.fromNumeric( (1,2,3,4,5)),
			),
			(
				'1....  somewhere(2). \n3.this(4).5..',
				oid.OID.fromNumeric( (1,2,3,4,5)),
			),
		]:
			assert oid.OID( source ) == expected, (source,expected)
	def test_tuple( self ):
		"""Can we coerce properly from a tuple?"""
		for source,expected in [
			(
				(1,2,3,4,5),
				oid.OID.fromNumeric( (1,2,3,4,5)),
			),
			(
				[1,2,3,4,5],
				oid.OID.fromNumeric( (1,2,3,4,5)),
			),
			(
				[1,],
				oid.OID( '.1' ),
			),
		]:
			assert oid.OID( source ) == expected, (source,expected)
	def test_slice( self ):
		"""Can we slice an OID?"""
		o = oid.OID( '.1.2.3.4.5' )
		b = o[:3]
		assert b == (1,2,3), b
		assert isinstance( b, oid.OID ), b
		assert o[4] == 5L, o[4]
		c = o[1:5]
		assert c == (2,3,4,5)
		assert not isinstance( c, oid.OID )
	def test_str( self ):
		"""Can we convert to a reasonable representation?"""
		o = oid.OID( '.1.2.3.4.5' )
		assert str(o) == '.1.2.3.4.5', str(o)
		o = oid.OID( '.1.2. this(3).4.5' )
		assert str(o) == '.1.2.this(3).4.5', str(o)

	def test_eq( self ):
		o = oid.OID( '.1.2.3.4.5' )
		assert o == '.1.2.3.4.5'
		assert o == (1,2,3,4,5)
		assert o == [1,2,3,4,5]
		assert o == oid.OID([1,2,3,4,5])


if __name__ == "__main__":
	unittest.main()