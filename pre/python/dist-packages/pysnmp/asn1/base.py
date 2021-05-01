"""
   A framework for implementing ASN.1 data types.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
# Module public names
__all__ = [ 'tagClasses', 'tagFormats', 'tagCategories', 'SimpleAsn1Object', \
            'RecordTypeAsn1Object', 'ChoiceTypeAsn1Object', \
            'VariableTypeAsn1Object' ]

try:
    from sys import version_info
except ImportError:
    version_info = (0,0)
from operator import getslice, setslice, delslice
try:
    enumerate
except NameError:
    def enumerate( iterable ):
        i = 0
        for x in iterable:
            yield i,x
            i+=1

from types import *
from pysnmp.asn1 import error
from pysnmp.error import PySnmpError
import operator

# ASN.1 tagging

tagClasses = { 
    'UNIVERSAL'          : 0x00,
    'APPLICATION'        : 0x40,
    'CONTEXT'            : 0x80,
    'PRIVATE'            : 0xC0
    }

tagFormats = {
    'SIMPLE'             : 0x00,
    'CONSTRUCTED'        : 0x20
    }

tagCategories = {
    'IMPLICIT'           : 0x01,
    'EXPLICIT'           : 0x02,
    'UNTAGGED'           : 0x04
    }

class Asn1Object:
    """Base class for all ASN.1 objects
    """
    #
    # ASN.1 tags
    #
    tagClass = tagClasses['UNIVERSAL']
    tagFormat = None
    tagId = None
    tagCategory = tagCategories['IMPLICIT']
    
    #
    # Argument type constraint
    #
    allowedTypes = ()

    #
    # Subtyping stuff
    #

    # A list of constraints.Constraint instances for checking values
    constraints = ()

    def _subtype_constraint(self, value):
        """All constraints checking method
        """
        for c in self.constraints:
            c( self, value )
        return
                
    def _type_constraint(self, value):
        """Constraint checking to see if value is of an acceptable type
        """
        if self.allowedTypes:
            if not isinstance(value, self.allowedTypes):
                raise error.ValueConstraintError('Value type constraint for %s: %s not in %s' % (self.__class__.__name__, type(value), str(self.allowedTypes)))
        
    def getUnderlyingTag(self):
        """
        """
        for superClass in self.__class__.__bases__:
            if issubclass(self.__class__, superClass):
                break
        else:
            raise error.BadArgumentError('No underlying type for %s' % \
                                         self.__class__.__name__)

        return (superClass.tagClass, superClass.tagFormat, superClass.tagId)

class SimpleAsn1Object(Asn1Object):
    """Base class for a simple ASN.1 object. Defines behaviour and
       properties of various non-structured ASN.1 objects.
    """
    tagFormat = tagFormats['SIMPLE']
    tagId = 0x00
    initialValue = None

    # Disable not applicible constraints
    _subtype_inner_subtype_constraint = None
    
    def __init__(self, value=None):
        """Store ASN.1 value
        """
        self.set(value)

    def __str__(self):
        """Return string representation of class instance
        """
        return '%s: %s' % (self.__class__.__name__, str(self.get()))

    def __repr__(self):
        """Return native representation of instance payload
        """
        return self.__class__.__name__ + '(' + repr(self.get()) + ')'

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if hasattr(self, '_cmp'):
            return self._cmp(other)
        if isinstance(other, SimpleAsn1Object):
            if not isinstance(other, self.__class__):
                try:
                    other = self.componentFactoryBorrow(other.get())
                except PySnmpError:
                    # Hide coercion errors
                    return -1
        else:
            try:
                other = self.componentFactoryBorrow(other)
            except PySnmpError:
                # Hide coercion errors
                return -1
        return cmp(self.rawAsn1Value, other.rawAsn1Value)

    def __hash__(self):
        """Returns hash of the payload value
        """
        try:
            return hash(self.rawAsn1Value)

        except TypeError:
            # Attempt to hash sequence value
            return reduce(operator.xor, map(hash, self.rawAsn1Value),
                          hash(None))

    def __nonzero__(self):
        """Returns true if value is true
        """
        if self.rawAsn1Value:
            return 1
        else:
            return 0

    # caching types for _setRawAsn1Value instead of rebuilding tuple
    # for each call (minor speedup)
    NORMAL_STATIC_TYPES = (IntType,LongType,StringType,NoneType,FloatType,TupleType)
    def _setRawAsn1Value(self, value):
        self._subtype_constraint(value)

        # Supported mutable type            
        if isinstance( value, list ):
            # Copy mutable object
            # XXX This line is most of the overhead of the method, doesn't
            # seem ammenable to optimisation?  Other than possibly watching
            # for cases where we could optimise away the copy?
            # That would require tracking (boolean) whether we know the value
            # has been created anew for us, I'm guessing that in most cases
            # it already has been?  Something to look at later.
            self.rawAsn1Value = value[:]
        # Supported immutable types
        elif isinstance( value, self.NORMAL_STATIC_TYPES):
            self.rawAsn1Value = value
        else:
            raise error.BadArgumentError('Unsupported value type to hold at %s: %s' % (self.__class__.__name__, valType))

    def componentFactoryBorrow(self, value=None):
        if not hasattr(self, '_componentCache'):
            self._componentCache = self.__class__()
        if value is not None: self._componentCache.set(value)
        return self._componentCache
        
    #
    # Simple ASN.1 object protocol definition
    #

    def set(self, value):
        """Set a value to object
        """
        if value is None:
            initial = self.initialValue
            if callable(initial):
                return initial()
            elif initial is None:
                self.rawAsn1Value = initial
                return
            value = initial
        # Allow initalization from instances
        if isinstance(value, SimpleAsn1Object):
            # Save on same-type instances
            if isinstance(value, self.__class__):
                self._setRawAsn1Value(value.rawAsn1Value)
            else:
                self.set(value.get())
            return
            self._type_constraint(value)
        if hasattr(self, '_iconv'):
            value = self._iconv(value)
        self._setRawAsn1Value(value)
        
    def get(self):
        """Get a value from object
        """
        if hasattr(self, '_oconv'):
            return self._oconv(self.rawAsn1Value)
        
        return self.rawAsn1Value

    # XXX left for compatibility
    def getTerminal(self): return self
    
class StructuredAsn1Object(Asn1Object):
    """Base class for structured ASN.1 objects
    """
    tagFormat = tagFormats['CONSTRUCTED']
    
    # Disable not applicible constraints
    _subtype_value_range_constraint = None
    _subtype_permitted_alphabet_constraint = None

class FixedTypeAsn1Object(StructuredAsn1Object):
    """Base class for fixed-type ASN.1 objects
    """
    # Disable not applicible constraints
    _subtype_size_constraint = None

    def __init__(self):
        """Initialize object internals
        """
        # Dictionary emulation (for strict ordering)
        self._names = []
        self._components = {}

    def __str__(self):
        """Return string representation of class instance
        """
        s = ', '.join( [
            '%s: %s' % (name, self._components[name])
            for name in self._names
        ])
        return '%s: %s' % (self.__class__.__name__, s)

    def __repr__(self):
        """Return native representation of instance payload
        """
        s = ', '.join( [
            '%s = %r' % (name, self._components[name])
            for name in self._names
        ])
        return '%s(%s)' % (self.__class__.__name__, s)

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if hasattr(self, '_cmp'):
            return self._cmp(other)

        if type(other) == InstanceType and isinstance(other, FixedTypeAsn1Object):
            return cmp(self._names, other._names) | \
                   cmp(self._components, other._components)
        else:
            # Hide coercion errors
            return -1

    def __hash__(self):
        """Returns hash of the payload value
        """
        return reduce(operator.xor, map(hash, self._names) +
                      map(hash, self.values()), hash(None))

    #
    # Mapping object protocol (re-implemented for strict ordering)
    #

    def __getitem__(self, key):
        """Return component by key
        """
        return self._components[ key ]

    def keys(self):
        """Return a list of keys
        """
        return self._names

    def has_key(self, key):
        """Return true if key exists
        """
        return self._components.has_key( key )
    
    def values(self):
        """Return a list of values
        """
        return map( self._components.__getitem__, self._names )

    def items(self):
        """Return a list of tuples (key, value)
        """
        return [
            (name,self._components[name])
            for name in self._names
        ]

    def update(self, dict):
        """Merge dict to ourselves
        """
        for key in dict.keys():
            self[key] = dict[key]

    def get(self, key, default=None):
        """Lookup by key with default
        """
        if self.has_key(key):
            return self[key]
        else:
            return default
        
    def __len__(self):
        """Get length of the object"""
        return len(self._components)

class RecordTypeAsn1Object(FixedTypeAsn1Object):
    """Base class for fixed-structure ASN.1 objects
    """
    fixedNames = []
    fixedComponents = []
    
    def __init__(self, **kwargs):
        """Store dictionary args
        """
        FixedTypeAsn1Object.__init__(self)

        # Initialize fixed structure
        for name,component in zip(self.fixedNames,self.fixedComponents):
            self._names.append( name )
            self._components[name] = component()

        self.update(kwargs)

    #
    # Mapping object protocol (re-implemented for strict ordering)
    #

    def __setitem__(self, key, value):
        """Set component by key & value
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s'\
                                         % (repr(value), \
                                            self.__class__.__name__))

            self._type_constraint(value)
            self._subtype_constraint(value)

        # XXX
        if self._components.has_key( key ):
            if not isinstance(value, self._components[key].__class__):
                raise error.BadArgumentError(
                    'Component type mismatch: %s vs %s' % (
                        self._components[key].__class__.__name__,
                        value.__class__.__name__
                    )
                )
            self._components[key] = value

        else:
            raise error.BadArgumentError('No such identifier %s at %s' %\
                                         (key, self.__class__.__name__))

class ChoiceTypeAsn1Object(FixedTypeAsn1Object):
    """Base class for choice-type ASN.1 objects
    """
    choiceNames = []
    choiceComponents = []
    initialComponent = None
    
    def __init__(self, **kwargs):
        """Store dictionary args
        """
        FixedTypeAsn1Object.__init__(self)
        if len(kwargs) == 0 and self.initialComponent is not None:
            kwargs[''] = self.initialComponent()
        self.update(kwargs)

    def componentFactoryBorrow(self, key):
        if not hasattr(self, '_componentCache'):
            self._componentCache = {}
        if not self._componentCache.has_key(key):
            try:
                self._componentCache[key] = self.choiceComponents[\
                    self.choiceNames.index(key)]()
            except (ValueError, IndexError):
                raise error.BadArgumentError('Non-existing key %s' % key)
        return self._componentCache[key]

    #
    # Dictionary interface emulation (for strict ordering)
    #

    def __setitem__(self, key, value):
        """Set component by key & value
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN.1 assignment at %s: %s'\
                                         % (self.__class__.__name__,
                                            repr(value)))

            self._type_constraint(value)
            self._subtype_constraint(value)

        for index,choiceComponent in enumerate(self.choiceComponents):
            if isinstance(value, choiceComponent):
                self._components = { self.choiceNames[index]: value }
                try:
                    self._names = [ self.choiceNames[index] ]
                except IndexError:
                    self._names = [ str(choiceComponent.__name__) ]
                return
        raise error.BadArgumentError(
            'Unexpected component type %s at %s'% (
                value.__class__.__name__,
                self.__class__.__name__
            )
        )

    def __delitem__(self, key):
        """Delete component by key
        """
        try:
            idx = self._names.index(key)

        except ValueError:
            raise KeyError, str(key)

        else:
            del self._names[idx]
            del self._components[key]

class AnyTypeAsn1Object(FixedTypeAsn1Object):
    """Base class for any-type ASN.1 objects
    """
    initialComponent = None
    
    def __init__(self, **kwargs):
        """Store dictionary args
        """
        FixedTypeAsn1Object.__init__(self)
        if len(kwargs) == 0 and self.initialComponent is not None:
            kwargs[''] = self.initialComponent()
        self.update(kwargs)

    #
    # Dictionary interface emulation (for strict ordering)
    #

    def __setitem__(self, key, value):
        """Set component by key & value
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN.1 assignment at %s: %s'\
                                         % (self.__class__.__name__,
                                            repr(value)))

            self._type_constraint(value)
            self._subtype_constraint(value)

        # Drop possibly existing values as it is of a CHOICE nature
        del self._names[:]
        self._components.clear()
        self._names.append( key )
        self._components[ key ] = value 

    def __delitem__(self, key):
        """Delete component by key
        """
        try:
            idx = self._names.index(key)

        except ValueError:
            raise KeyError, str(key)

        else:
            del self._names[idx]
            del self._components[key]

class VariableTypeAsn1Object(StructuredAsn1Object):
    """Base class for variable-structure ASN.1 objects
    """
    # The only carried type
    protoComponent = None

    # Initial arguments to 'protoComponent'
    initialValue = []
    
    def __init__(self, *args):
        """Store possible components
        """
        # List emulation
        self._components = []
        args = list(args)
        if len(args) == 0:
            for val in self.initialValue:
                args.append(val())
        self.extend(args)

    def __str__(self):
        """Return string representation of class instance
        """
        s = ''
        for idx in range(len(self)):
            if s:
                s = s + ', '
            s = s + '%s' % str(self._components[idx])
        return '%s: %s' % (self.__class__.__name__, s)

    def __repr__(self):
        """Return native representation of instance payload
        """
        s = ''
        for idx in range(len(self)):
            if s:
                s = s + ', '
            s = s + '%s' % repr(self._components[idx])
        return '%s(%s)' % (self.__class__.__name__, s)

    def __cmp__(self, other):
        """Attempt to compare the payload of instances of the same class
        """
        if hasattr(self, '_cmp'):
            return self._cmp(other)

        if type(other) == InstanceType and \
               isinstance(other, VariableTypeAsn1Object):
            return cmp(self._components, other._components)
        else:
            # Hide coercion errors
            return -1

    def __hash__(self):
        """Returns hash of the payload value
        """
        return reduce(operator.xor, map(hash, self.values()),
                      hash(None))

    def componentFactoryBorrow(self):
        if not hasattr(self, '_componentCache'):
            self._componentCache = {}
        for uniqId in self._componentCache.keys():
            if self._componentCache[uniqId] is not None:
                c = self._componentCache[uniqId]
                self._componentCache[uniqId] = None
                return c
        c = self.protoComponent()
        self._componentCache[id(c)] = None
        return c

    def componentFactoryReturn(self, *vals):
        if not hasattr(self, '_componentCache'):
            self._componentCache = {}
        for val in vals:
            valId = id(val)
            if self._componentCache.has_key(valId):
                if self._componentCache[valId] is None:
                    self._componentCache[valId] = val
                else:
                    raise error.BadArgumentError('Extra component return %s'\
                                                 % val)

    #
    # Mutable sequence object protocol
    #

    def __setitem__(self, idx, value):
        """Set object by subscription
        """
        if type(idx) == SliceType:
            apply(self.componentFactoryReturn,
                  self._components[idx.start:idx.stop])            
            setslice(self._components, idx.start, idx.stop, list(value))
            return

        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s'\
                                         % (repr(value), \
                                            self.__class__.__name__))

        if type(self.protoComponent) != ClassType or \
           not isinstance(value, self.protoComponent):
            raise error.BadArgumentError('Unexpected component type %s at %s'\
                                         % (value.__class__.__name__, \
                                            self.__class__.__name__))

            self._type_constraint(value)
            self._subtype_constraint(value)

        self.componentFactoryReturn(self._components[idx])
        
        self._components[idx] = value

    def __getitem__(self, idx):
        """Get object by subscription
        """
        if type(idx) == SliceType:
            return getslice(self._components, idx.start, idx.stop)
        return self._components[idx]

    def __delitem__(self, idx):
        """Remove object by subscription
        """
        if type(idx) == SliceType:
            apply(self.componentFactoryReturn,
                  self._components[idx.start:idx.stop])
            delslice(self._components, idx.start, idx.stop)
            return        
        self.componentFactoryReturn(self._components[idx])
        del self._components[idx]

    if version_info < (2, 0):
        # They won't be defined if version is at least 2.0 final

        def __getslice__(self, i, j):
            return self[max(0, i):max(0, j):]
        def __setslice__(self, i, j, seq):
            self[max(0, i):max(0, j):] = seq
        def __delslice__(self, i, j):
            del self[max(0, i):max(0, j):]

    def append(self, value):
        """Append object to end
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s' %\
                                         (repr(value), \
                                          self.__class__.__name__))

        if type(self.protoComponent) != ClassType or \
           not isinstance(value, self.protoComponent):
            raise error.BadArgumentError('Unexpected component type %s at %s'\
                                         % (value.__class__.__name__, \
                                            self.__class__.__name__))

            self._type_constraint(value)
            self._subtype_constraint(value)

        self._components.append(value)

    def extend(self, values):
        """Extend list by appending list elements
        """
        if type(values) != ListType:
            raise error.BadArgumentError('Non-list arg to %s.extend: %s'\
                                         % (self.__class__.__name__,
                                            type(values)))
        for value in values:
            self.append(value)

    def insert(self, idx, value):
        """Insert object before index
        """
        # Hard-coded type constraint XXX
        if not isinstance(value, Asn1Object):
            raise error.BadArgumentError('Non-ASN1 object %s at %s' %\
                                         (repr(value),\
                                          self.__class__.__name__))

        if type(self.protoComponent) != ClassType or \
           not isinstance(value, self.protoComponent):
            raise error.BadArgumentError('Unexpected component type %s at %s'\
                                         % (value.__class__.__name__, \
                                            self.__class__.__name__))

            self._type_constraint(value)
            self._subtype_constraint(value)

        self._components.insert(idx, value)
        
    def pop(self, idx=None):
        """Remove and return item at index (default last)
        """
        c = self._components.pop(idx)
        self.componentFactoryReturn(c)
        return c

    def index(self, idx): return self._components.index(idx)
    def __len__(self): return len(self._components)

    def clear(self):
        apply(self.componentFactoryReturn, self._components)
        self._components = []
        
