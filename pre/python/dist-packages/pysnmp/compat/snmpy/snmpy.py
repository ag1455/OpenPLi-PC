"""
   Compatibility interface to the snmpy package. The degree of compatibility
   is mostly limited by the lack of MIB parser in PySNMP.

   For more information on snmpy project, please, refer to
   http://www.sf.net/projects/snmpy/

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.

   Initial copyrights for prototype code and API are as follows:

   Written by Anthony Baxter, arb@connect.com.au
   Copyright (C) 1994,1995,1996 Anthony Baxter.

   Modified extensively by Tim O'Malley, timo@bbn.com.
   The changes are Copyright (C) 1996 of BBN.
 
   Permission is hereby granted, free of charge, to any person obtaining
   a copy of this source file to use, copy, modify, merge, or publish it
   subject to the following conditions:

   The above copyright notice and this permission notice shall be included
   in all copies or in any new file that contains a substantial portion of
   this file.

   THE  AUTHOR  MAKES  NO  REPRESENTATIONS ABOUT  THE  SUITABILITY  OF
   THE  SOFTWARE FOR  ANY  PURPOSE.  IT IS  PROVIDED  "AS IS"  WITHOUT
   EXPRESS OR  IMPLIED WARRANTY.  THE AUTHOR DISCLAIMS  ALL WARRANTIES
   WITH  REGARD TO  THIS  SOFTWARE, INCLUDING  ALL IMPLIED  WARRANTIES
   OF   MERCHANTABILITY,  FITNESS   FOR  A   PARTICULAR  PURPOSE   AND
   NON-INFRINGEMENT  OF THIRD  PARTY  RIGHTS. IN  NO  EVENT SHALL  THE
   AUTHOR  BE LIABLE  TO  YOU  OR ANY  OTHER  PARTY  FOR ANY  SPECIAL,
   INDIRECT,  OR  CONSEQUENTIAL  DAMAGES  OR  ANY  DAMAGES  WHATSOEVER
   WHETHER IN AN  ACTION OF CONTRACT, NEGLIGENCE,  STRICT LIABILITY OR
   ANY OTHER  ACTION ARISING OUT OF  OR IN CONNECTION WITH  THE USE OR
   PERFORMANCE OF THIS SOFTWARE.
"""
from exceptions import Exception
from time import time
from types import ListType
from pysnmp.proto import v1
from pysnmp.mapping.udp import role
from pysnmp.asn1 import base
import pysnmp.error, pysnmp.mapping.udp.error

# Module exceptions
class SnmpError(Exception): pass
class SnmpTimeout(Exception): pass

# Module constants
version = 0.73
SNMP_TRAP_PORT = 162

class CompatBase:
    """Base class for compatibility classes
    """
    def _wrapper_fun(self, fun, *args):
        """
        """
        try:
            return apply(fun, args)

        # Catch transport-speciic, timeout exceptions

        except pysnmp.mapping.udp.error.NoResponseError, why:
            raise SnmpTimeout(why)

        except pysnmp.mapping.udp.error.IdleTimeoutError, why:
            raise SnmpTimeout(why)

        # Render the rest of PySNMP exceptions to one
        except pysnmp.error.PySnmpError, why:
            raise SnmpError(why)

class snmpmibnode(CompatBase):
    """A single MIB object (variable-binding)
    """
    def __init__(self, parent, name, extension):
        """Class constructor: initialize object internals from passed OID
        """
        self._wrapper_fun(self._init_fun, parent, name, extension)

    def _init_fun(self, parent, name, extension):
        """The backend method for class constructor
        """
        oid = ''
        try:
            if name[0] != '.':
                oid = '.1.3.6.1.2.1'
            oid = '%s.%s' % (oid, name)
            if extension:
                oid = '%s.%s' % (oid, extension)
        except:
            raise SnmpError('Malformed OID name/extension: %s/%s' %
                            (name, extension))

        # Keep a real OID object around
        self._oid = v1.ObjectIdentifier(oid)
        self._value = None
        self._session = parent

    def __getattr__(self, attr):
        """Translate some attributes
        """
        return self._wrapper_fun(self._getattr_fun, attr)

    def _getattr_fun(self, attr):
        """Backend for __getattr__ method
        """
        if attr == 'oid':
            return self._oid.get()
        elif attr == 'name':
            return self.oid
        elif attr == 'index':
            return 0L
        elif attr == 'value':
            if self._value is None:
                return None
            else:
                self._value.get()
        elif attr == 'type':
            # More types to add?
            if self._value is None:
                return 0
            else:
                if isinstance(self._value, v1.ObjectIdentifier):
                    return 1
                elif isinstance(self._value, v1.OctetString):
                    return 2
                elif isinstance(self._value, v1.Integer):
                    return 3
                elif isinstance(self._value, v1.NetworkAddress):
                    return 4
                elif isinstance(self._value, v1.IpAddress):
                    return 5
                elif isinstance(self._value, v1.Counter):
                    return 6
                elif isinstance(self._value, v1.Gauge):
                    return 7
                elif isinstance(self._value, v1.TimeTicks):
                    return 8
                elif isinstance(self._value, v1.Opaque):
                    return 9
                elif isinstance(self._value, v1.Null):
                    return 10
                elif isinstance(self._value, v1.Counter64):
                    return 11
                # XXX may be continued
                else:
                    raise SnmpError('Unsupported value type: %s' %
                                    self._value)
        elif attr == 'session':
            return self._session
        elif attr == 'description':
            return ''
        elif attr == 'enums':
            raise SnmpError('Feature not implemented')

        raise AttributeError, attr

    def __setattr__(self, attr, val):
        """Set certain attributes
        """
        return self._wrapper_fun(self._setattr_fun, attr, val)
    
    def _setattr_fun(self, attr, val):
        """Backend for __setattr__ method 
        """
        if attr in ['oid', 'name', 'index', 'type', 'description', 'enums']:
            raise SnmpError('Read-only attribute: %s' % attr)
        elif attr == 'value':
            if not isinstance(val, base.SimpleAsn1Object):
                raise SnmpError('Non ASN1 object given for value: %s' \
                                % str(val))
            self._value = val

        self.__dict__[attr] = val

    def __repr__(self):
        """Try to look similar to original implementation
        """
        return self._wrapper_fun(self._repr_fun)
        
    def _repr_fun(self):
        """Backend for __repr__ method
        """
        return '<SNMP_mibnode %s, %u, %s>' % (self.name, self.type, self.value)

    # Mapping object API

    def __len__(self):
        """Returns number of sub-OIDs in SNMP table (can't be implemented
           w/o MIB parser)
        """
        return 0

    def __getitem__(self, key):
        """Support creating child OIDs by subscription
        """
        return self._wrapper_fun(self._getitem_fun, key)
        
    def _getitem_fun(self, key):
        """Backend for __getitem__ method
        """
        try:
            key = '%u' % key
        except:
            pass

        return snmpmibnode(self._session, self.oid, key)

    def __setitem__(self, key, value):
        """Support creating child OIDs by subscription
        """
        return self._wrapper_fun(self._setitem_fun, key, value)
        
    def _setitem_fun(self, key, value):
        """Backend for __setitem__ method
        """
        try:
            key = '%u' % key
        except:
            pass

        self._session.set(self[key], value)

    # Indirect access to session object

    def get(self):
        """Indirect GET request access to parent session object
        """
        return self._session.get(self.oid)

    def getnext(self):
        """Indirect GETNEXT request access to parent session object
        """
        return self._session.getnext(self.oid)

    def set(self, val):
        """Indirect SET request access to parent session object
        """
        return self._session.set(self.oid, val)

    # Misc ops on OID object
    
    def oidlist(self):
        """Return a list of sub-OIDs
        """
        return list(self._oid)

    def nodes(self):
        """Return child sub-nodes
        """
        raise SnmpError('Feature not implemented')

    def enums(self):
        """Not clear what this does so far
        """
        raise SnmpError('Feature not implemented')

class snmptrap(CompatBase):
    """A SNMP TRAP request object
    """
    def __init__(self, parent, addr, name, trap_type, specific_type,
                 uptime, varbind):
        """Class constructor: initialize object internals from passed params
        """        
        self._wrapper_fun(self._init_fun, parent, addr, name, trap_type,
                          specific_type, uptime, varbind)
        
    def _init_fun(self, parent, addr, name, trap_type, specific_type,
                  uptime, varbind):
        """Backend for __init__ method
        """
        # Keep a real Trap object around
        self.req = v1.Trap()
        self.req['pdu']['trap']['agent_addr']['internet'].set(addr)
        self.req['pdu']['trap']['enterprise'].set(name)
        self.req['pdu']['trap']['generic_trap'].set(trap_type)
        self.req['pdu']['trap']['specific_trap'].set(specific_type)
        self.req['pdu']['trap']['time_stamp'].set(uptime)
        self.req['pdu']['trap']['variable_bindings'] = varbind

        # Non-masked public attributes
        self._session = parent

    def __getattr__(self, attr):
        """Translate some attributes
        """
        return self._wrapper_fun(self._getattr_fun, attr)
    
    def _getattr_fun(self, attr):
        """Backend for __getattr__ method
        """
        if attr == 'addr':
            return self.req['pdu']['trap']['agent_addr']['internet'].get()
        elif attr == 'oid':
            return self.req['pdu']['trap']['enterprise'].get()
        elif attr == 'name':
            return self.oid
        elif attr == 'type':
            return self.req['pdu']['trap']['generic_trap'].get()
        elif attr == 'specific_type':
            return self.req['pdu']['trap']['specific_trap'].get()
        elif attr == 'uptime':
            return self.req['pdu']['trap']['time_stamp'].get()
        elif attr == 'session':
            return self._session
        elif attr == 'variables':
            # Fetch Object ID's and associated values
            oids = map(lambda x: x['name'].get(), \
                       self.req['pdu'].values()[0]['variable_bindings'])
            vals = map(lambda x: x['value'].values()[0].values()[0], \
                       self.req['pdu'].values()[0]['variable_bindings'])

            miboids = []
            for oid, val in map(None, oids, vals):
                miboid = snmpmibnode(self, oid, None)
                miboid.value = val
                miboids.append(miboid)

            if len(miboids) == 1:
                return miboids[0]
            else:        
                return miboids

        raise AttributeError, attr

    def __setattr__(self, attr, val):
        """Set certain attributes
        """
        return self._wrapper_fun(self._setattr_fun, attr, val)

    def _setattr_fun(self, attr, val):
        """Backend for __setattr__ method
        """
        if attr in ['addr', 'oid', 'name', 'type', 'specific_type',
                    'uptime', 'session', 'variables']:
            raise SnmpError('Read-only attribute: %s' % attr)

        self.__dict__[attr] = val

    def __repr__(self):
        """Try to look similar to original implementation
        """
        return self._wrapper_fun(self._repr_fun)
        
    def _repr_fun(self):
        """Backend for __repr__ method
        """
        return '<SNMP_trap %s, %s, type=%d, stype=%d, uptime=%d>' % \
               (self.addr, self.name, self.type, \
                self.specific_type, self.uptime)

# A repository of pending async sessions
pendingSessions = {}

class SNMP_Session(CompatBase):
    """SNMP session object
    """
    def __init__(self, hostname, community='public', remote_port=0,
                 local_port=0, retries=0, timeout=0, callback=None):
        """Initialize transport layer, store passed args
        """
        return self._wrapper_fun(self._init_fun, hostname, community,
                                 remote_port, local_port, retries, timeout,
                                 callback)

    def _init_fun(self, hostname, community, remote_port, local_port,
                  retries, timeout, callback):
        """Backend for __init__ method
        """
        # Set defaults
        if hostname is None: hostname = '0.0.0.0'
        if community is None: community = 'public'
        if remote_port == 0: remote_port = 161
        if retries == 0: retries = 3
        if timeout == 0: timeout = 3
        if callback is not None and not callable(callback):
            raise SnmpError('Non-callable callback function')
 
        if local_port == 0:
            # Create SNMP manager object
            self.mgr = role.manager((hostname, remote_port))
            self.mgr.open()
            self.mgr.retries = retries
            self.mgr.timeout = timeout
            self.agt = None
        else:
            if callback is None:
                raise SnmpError('Agent role requires callback function')

            # Create SNMP agent object
            self.agt = role.agent((callback, None), [(hostname, local_port)])
            self.agt.open()
            self.mgr = None

        # Expose public attributes
        self.addr = hostname
        self.community = community
        self.timeout = timeout
        self.remote_port = remote_port
        self.local_port = local_port
        self.retries = retries
        self.callback = callback

        # A repository of pending SNMP reqs (for async use)
        self.pendingReqs = {}

    def _request(self, oid, req, val=[v1.ObjectSyntax()]):
        """Performs a get request
        """
        if self.mgr is None:
            raise SnmpError('Agent role is active')

        # Convert to list if not done yet
        if type(oid) != ListType:
            oid = [ oid ]
       
        for idx in range(len(oid)):
            if isinstance(oid[idx], snmpmibnode):
                oid[idx] = oid[idx].oid
 
        # Add community name
        req['community'].set(self.community)

        # Build and set Object ID & variables bindings
        req['pdu'].values()[0]['variable_bindings'].extend(
            map(lambda x, y, self=self: v1.VarBind(
            name=v1.ObjectName(x), value=y), oid, val))

        # Encode SNMP request message, send it to SNMP agent        
        if self.callback is None:
            # ...and receive a response
            (answer, src) = self.mgr.send_and_receive(req.encode())
        else:
            # Register pending request
            self.pendingReqs[req] = time() + self.timeout

            # Register pending session
            if not pendingSessions.has_key(self):
                pendingSessions[self] = 1

            # Send request message
            return self.mgr.send(req.encode())

        # Decode SNMP response
        rsp = v1.GetResponse(); rsp.decode(answer)

        # Make sure response matches request
        if not req.match(rsp):
            raise GetError('Unmatched response: %s vs %s' % (req, rsp))

        # Fetch Object ID's and associated values
        oids = map(lambda x: x['name'].get(), \
                   rsp['pdu'].values()[0]['variable_bindings'])
        vals = map(lambda x: x['value'].values()[0].values()[0], \
                   rsp['pdu'].values()[0]['variable_bindings'])

        # Check for remote SNMP agent failure
        if rsp['pdu'].values()[0]['error_status']:
            raise SnmpError(str(rsp['pdu'].values()[0]['error_status']) + \
                            ' at ' + str(oids[rsp['pdu'].values()[0]
                                              ['error_index'].get()-1]))

        miboids = []
        for oid, val in map(None, oids, vals):
            miboid = snmpmibnode(self, oid, None)
            miboid.value = val
            miboids.append(miboid)

        if len(miboids) == 1:
            return miboids[0]
        else:        
            return miboids

    def get(self, oid):
        """Perform SNMP GET request
        """
        return self._wrapper_fun(self._get_fun, oid)

    def _get_fun(self, oid):
        """Backend for get method
        """
        return self._request(oid, v1.GetRequest())

    def getnext(self, oid):
        """Perform SNMP GETNEXT request
        """
        return self._wrapper_fun(self._getnext_fun, oid)

    def _getnext_fun(self, oid):
        """Backend for getnext method
        """
        return self._request(oid, v1.GetNextRequest())

    # A strange allias
    thepowerfulgetnext = getnext

    def set(self, oid, val, valType='string'):
        """Perform SNMP SET request
        """
        return self._wrapper_fun(self._set_fun, oid, val, valType)

    def _set_fun(self, oid, val, valType):
        """Backend for set method
        """
        valObj = None
        for syntax in [ v1.SimpleSyntax, v1.ApplicationSyntax]:
            for (objName, objType) in map(None, syntax.choiceNames,
                                          syntax.choiceComponents):
                if valType == objName:
                    valObj = v1.ObjectSyntax(syntax=syntax(value=objType(val)))
                    break
                
        if valObj is None:
            raise SnmpError('Unknown ASN.1 value type name: %s' % valType)
        
        return self._request(oid, v1.SetRequest(), [ valObj ])

    def mibnode(self, name, extension=None):
        """Return a MIBNODE object
        """
        return snmpmibnode(self, name, extension)

    def fileno(self):
        """Return transport fileno
        """
        return self._wrapper_fun(self._fileno_fun)

    def _fileno_fun(self):
        """Backend for fileno method
        """
        if self.mgr is not None:
            return self.mgr.get_socket().fileno()
        if self.agt is not None:
            return self.agt.get_socket().fileno()
        raise SnmpError('Transport level not initialized')      

    def read(self):
        """Read SNMP response from transport level, decode it and
           invoke the callback routine
        """
        return self._wrapper_fun(self._read_fun)

    def _read_fun(self):
        """Backend for read method
        """
        if self.mgr is not None:
            (answer, src) = self.mgr.read()
        elif self.agt is not None:
            (answer, src) = self.agt.read()

            rsp = v1.Trap(); rsp.decode(answer)

            return self.callback(
                snmptrap(self, rsp['pdu']['trap']\
                         ['agent_addr']['internet'].get(),
                         rsp['pdu']['trap']['enterprise'].get(),
                         rsp['pdu']['trap']['generic_trap'].get(),
                         rsp['pdu']['trap']['specific_trap'].get(),
                         rsp['pdu']['trap']['time_stamp'].get(),
                         rsp['pdu']['trap']['variable_bindings']))
        else:
            raise SnmpError('Transport level not initialized')

        rsp = v1.GetResponse(); rsp.decode(answer)

        # Make sure response matches any of pending requests
        for req in self.pendingReqs.keys():
            if req.match(rsp):
                del self.pendingReqs[req]
                if len(self.pendingReqs) == 0:
                    del pendingSessions[self]
                break
        else:
            raise SnmpError('Unmatched response: %s' % rsp)

        # Fetch Object ID's and associated values
        oids = map(lambda x: x['name'].get(), \
                   rsp['pdu'].values()[0]['variable_bindings'])
        vals = map(lambda x: x['value'].values()[0].values()[0], \
                   rsp['pdu'].values()[0]['variable_bindings'])

        # Check for remote SNMP agent failure
        if rsp['pdu'].values()[0]['error_status']:
            raise SnmpError(str(rsp['pdu'].values()[0]['error_status']) + \
                            ' at ' + str(oids[rsp['pdu'].values()[0]
                                              ['error_index'].get()-1]))

        miboids = []
        for oid, val in map(None, oids, vals):
            miboid = snmpmibnode(self, oid, None)
            miboid.value = val
            miboids.append(miboid)

        if len(miboids) == 1:
            return self.callback(miboids[0])
        else:        
            return self.callback(miboids)        

# Module functions

def session(hostname, community, remote_port, local_port, retries,
            timeout, callback=None):
    """Return SNMP session object
    """
    return SNMP_Session(hostname, community, remote_port, local_port,
                        retries, timeout, callback)
    
def checkoid(oid):
    """Return true if given OID is syntaxically valid XXX
    """
    try:
        v1.ObjectIdentifier(oid)
        
    except:
        return 0

    return 1

def issuboid(miboid1, miboid2):
    """Compare two MIB oids, return 1 if equal
    """
    if isinstance(miboid1, snmpmibnode):
        miboid1 = miboid1.oid
    if isinstance(miboid2, snmpmibnode):
        miboid2 = miboid2.oid

    try:
        if v1.ObjectIdentifier(miboid1) == v1.ObjectIdentifier(miboid2):
            return 1
        else:
            return 0

    except pysnmp.error.PySnmpError, why:
        raise SnmpError(why)

def merge(filename):
    """Load and parse MIB file
    """
    raise NotImplementedError('merge: function not implemented')

def addmibdir():
    """Add a path to MIB search path
    """
    raise NotImplementedError('addmibdir: function not implemented')

def timeout():
    """Return the estimated time till timeout
    """
    raise NotImplementedError('timeout: function not implemented')

def handletimeout():
    """Expire long pending SNMP requests
    """
    now = time()

    # Walk over pending sessions & reqs
    for ses in pendingSessions.keys():
        for req in ses.pendingReqs.keys():
            if ses.pendingReqs[req] < now:
                del ses.pendingReqs[req]
                if len(ses.pendingReqs) == 0:
                    del pendingSessions[ses]
                raise SnmpTimeout(req)
