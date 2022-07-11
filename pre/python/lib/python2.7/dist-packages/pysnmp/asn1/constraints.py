"""Constraint functions/objects for pysnmp

Constraints are relatively rare, but every ASN1 object
is doing checks all the time for whether they have any
constraints and whether they are applicable to the object.

What we're going to do is define objects/functions that
can be called unconditionally if they are present, and that
are simply not present if there are no constraints.
"""
from pysnmp.asn1 import error
__metaclass__ = type

class Constraint:
	"""Abstract base-class for constraint objects

	Constraints should be stored in a simple sequence in the
	namespace of their client Asn1Object sub-classes.
	"""
	def __call__( self, client, value ):
		"""Raise errors if value not appropriate for client"""

class SingleValueConstraint(Constraint):
	"""Value must be part of defined set constraint"""
##	__slots__ = ('values',)
	def __init__( self, *set ):
		"""Initialise the SingleValueConstraint with items

		*set -- hashable objects allowed
		"""
		self.values = dict([(x,1) for x in set])
	def __call__( self, client, value ):
		"""Raise errors if value not appropriate for client"""
		if not self.values.get( value ):
			raise error.ValueConstraintError(
				'%s for %r: value %s not within allowed values: %s' % (
					self.__class__.__name__,
					client.__class__.__name__,
					str(value),
					self.values.keys(),
				)
			)
		return 1
PermittedAlphabetConstraint = SingleValueConstraint

class ValueRangeConstraint(Constraint):
	"""Value must be within start and stop values (inclusive)"""
##	__slots__ = ('start','stop')
	def __init__( self, start, stop ):
		"""Initialise the SingleValueConstraint with items

		start -- value below which errors are raised
		stop -- value above which errors are raised
		"""
		if start > stop:
			stop,start = start,stop
		self.start,self.stop = start, stop
	def __call__( self, client, value ):
		"""Raise errors if value not appropriate for client"""
		if value < self.start or value > self.stop:
			raise error.ValueConstraintError(
				'%s for %r: value %s not within allowed range: %s through %s' % (
					self.__class__.__name__,
					client.__class__.__name__,
					str(value),
					self.start,
					self.stop,
				)
			)
		return 1

class ValueSizeConstraint( ValueRangeConstraint ):
	"""len(value) must be within start and stop values (inclusive)"""
##	__slots__ = ('start','stop')
	def __call__( self, client, value ):
		"""Raise errors if value not appropriate for client"""
		length = len(value)
		if length < self.start or length > self.stop:
			raise error.ValueConstraintError(
				'%s for %r: len(value) %s (%s) not within allowed range: %s through %s' % (
					self.__class__.__name__,
					client.__class__.__name__,
					str(value),
					length,
					self.start,
					self.stop,
				)
			)
		return 1

def ValueRangeConstraint( start, stop ):
	"""Construct a callable object for checking value-range within start:stop inclusive"""
	def _ValueRangeConstraint( client, value, start=start,stop=stop):
		if value < start or value > stop:
			raise error.ValueConstraintError(
				'ValueRangeConstraint for %r: value %s not within allowed range: %s through %s' % (
					client.__class__.__name__,
					str(value),
					start,
					stop,
				)
			)
		return 1
	return _ValueRangeConstraint

def ValueSizeConstraint( start, stop ):
	"""Construct a callable object for checking value-range within start:stop inclusive"""
	def _ValueSizeConstraint( client, value, start=start,stop=stop):
		length = len(value)
		if length < start or length > stop:
			raise error.ValueConstraintError(
				'ValueSizeConstraint for %r: len(value) %s (%s) not within allowed range: %s through %s' % (
					client.__class__.__name__,
					str(value),
					length,
					start,
					stop,
				)
			)
		return 1
	return _ValueSizeConstraint
