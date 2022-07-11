import types

def doJoin( a, b ):
	"""Join a and b with a single ."""
	if a.endswith( '.' ):
		if not b.startswith( '.' ):
			return a+b
		else:
			return a+b[1:]
	else:
		if not b.startswith( '.' ):
			return '%s.%s'%(a,b)
		else:
			return a+b

class OID( tuple ):
	"""SNMP OID object with minimal overhead"""
	def __new__( cls, *values ):
		if len(values) == 1 and not isinstance(values[0], (int,long)):
			values = values[0]
		if isinstance( values, (str,unicode)):
			return cls.fromString( values )
		elif isinstance( values, cls ):
			return values
		elif isinstance( values, (list,tuple)):
			return cls.fromNumeric( values )
		else:
			raise TypeError(
				"""Only know how to convert string, unicode, tuple or list, got %s""",
				type(values),
			)
	def fromCore( cls, stringForm, numericForm, aliases=None ):
		"""Create new OID object from string, numeric and aliases"""
		# we don't do anything with string by default...
		base = super( OID, cls ).__new__( cls, numericForm )
		base.aliases = aliases
		return base
	fromCore = classmethod( fromCore )
	def fromString( cls, value, aliases=None ):
		"""Convert string value to an OID value"""
		if value.find('(') < 0:
			try:
				numeric = [
					long(item,0)
					for item in value.split('.')
					if item.strip()
				]
			except ValueError:
				raise ValueError(
					"Malformed OID %r"%(value,)
				)
			else:
				return cls.fromCore( value, numeric )
		else:
			numeric = []
			encodedAliases = []
			for element in filter(None, value.split('.')):
				bracketIndex = element.find('(')
				if bracketIndex < 0:
					numeric.append(long(element,0))
					encodedAliases.append(None)
				else:
					encodedAliases.append(element[:bracketIndex].strip())
					element = element[
						bracketIndex+1:
						element.rindex(')')
					].strip()
					numeric.append(long(element,0))
			if aliases:
				aliases = [ (a or b) for (a,b) in map(None,encodedAliases,aliases)]
			else:
				aliases = encodedAliases or None
			return cls.fromCore( value, numeric, aliases )
	fromString = classmethod(fromString )
	def fromNumeric( cls, values, aliases=None ):
		"""Convert sequence of integer values to OID value"""
		values = map( long, values )
		if aliases is not None:
			if len(aliases)<len(values):
				aliases = aliases + [None]*(len(values)-len(aliases))
			elif len(aliases)>len(values):
				aliases = aliases[:len(values)]
		return cls.fromCore( None, values, aliases )
	fromNumeric = classmethod(fromNumeric )

	def __cmp__( self, other ):
		"""Compare to another object"""
		if not isinstance( other, OID ):
			try:
				other = self.__class__( other )
			except Exception, err:
				pass
		return cmp(tuple(self), other )
	def __add__( self, other ):
		"""Add something to us, creating a new OID"""
		if isinstance( other, OID ):
			return self.fromCore(
				None,
				tuple(self) + tuple(other),
				self.mergeAliases(other),
			)
		elif isinstance( other, (list,tuple)):
			return self.fromNumeric(
				tuple(self) + tuple(other),
				self.aliases
			)
		elif isinstance( other, (str,unicode)):
			otherObject = self.fromString( other )
			return self.fromString(
				doJoin(str(self),str(other)),
			)
		elif isinstance( other, (int,long)):
			return self.fromNumeric(
				tuple(self) + tuple(other),
				self.aliases,
			)
			
	def mergeAliases( self, otherObject ):
		"""Merge our aliases with another OID object"""
		if self.aliases:
			if otherObject.aliases:
				aliases = self.aliases + otherObject.aliases
			else:
				aliases = self.aliases + [None]*len(otherObject)
		elif otherObject.aliases:
			aliases = [None]*len(self)+ otherObject.aliases
		else:
			aliases = None
		return aliases

	def __getslice__( self, i,j,step=1, SLICETYPE=types.SliceType ):
		"""Retrieve an item or a slice of the OID

		if slice is an integer, return integer value

		if slice starts at 0, return an OID, otherwise
		just return a tuple.
		"""
		# Note that we are *not* using super for performance reasons,
		# that means that we don't play nicely with multiple inheritence
		# where someone wants to interpose themselves between us and tuple!
		slice = SLICETYPE( i,j, step )
		if slice.start == 0:
			# we already know our sub-values are valid sub-values
			# so we can use fromCore and avoid the calls to "long"
			return self.fromCore(
				None,
				tuple.__getitem__( self, slice ),
				self.aliases,
			)
		return tuple.__getitem__( self, slice )

	def __str__( self ):
		"""Get a bare string representation of this OID"""
		if self.aliases:
			result = ['']
			for num,name in map(None,self,self.aliases):
				if name is None:
					result.append(str(num))
				else:
					result.append( '%s(%d)'%(name,num))
			return ".".join(result)
		else:
			return "." + ".".join([str(num) for num in self])
	def __repr__( self ):
		"""Get a code-like representation of this OID"""
		return '%s( %r )'%( self.__class__.__name__, str(self))
	def isaprefix(self, other):
		"""Determine whether this OID is a prefix of other"""
		if not isinstance( other, OID ):
			other = self.__class__( other )
		if len(self) < len(other):
			if other[:len(self)] == self:
				return True
		return False

