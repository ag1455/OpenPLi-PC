"""
   Deprecated PySNMP 2.0.x compatibility interface to SNMP v.1
   protocol implementation.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.proto import v1
import pysnmp.proto.error, pysnmp.asn1.error, \
       pysnmp.asn1.encoding.ber.error
from pysnmp.compat.pysnmp2x import asn1

class Error(asn1.Error):
    """Base class for v1 module exceptions
    """
    pass

class TypeError(Error):
    """V1 data type incompatibility
    """
    pass

class BadArgument(Error):
    """Bad V1 object value
    """
    pass

class BadPDUType(Error):
    """Bad SNMP PDU type
    """
    pass

class BadVersion(Error):
    """Bad SNMP version
    """
    pass

class BadEncoding(Error):
    """Bad BER encoding in SNMP message
    """
    pass

class CompatBase:
    """Base class for compatibility classes
    """
    msgProto = None
    
    def __init__(self, **kwargs):
        """Compatibility constructor
        """
        self._wrapper_fun(self.__init_fun__, kwargs)

    def __init_fun__(self, kwdict):
        """Base class constructor
        """
        self.msg = self.msgProto()
        self.update(kwdict)
        
    def _wrapper_fun(self, fun, *args):
        """Call passed function and translate possible exceptions
        """
        try: 
            return apply(fun, args)           

        # Catch snmp package exceptions

        except pysnmp.proto.error.BadArgumentError, why:
            raise BadArgument(why)
       
        except pysnmp.proto.error.ProtoError, why:
            raise Error(why)        

        # Catch ber package exceptions
        
        except pysnmp.asn1.encoding.ber.error.BadArgumentError, why:
            raise asn1.BadArgument(why)

        except pysnmp.asn1.encoding.ber.error.TypeMismatchError, why:
            raise asn1.UnknownTag(why)

        except pysnmp.asn1.encoding.ber.error.OverFlowError, why:
            raise asn1.OverFlow(why)

        except pysnmp.asn1.encoding.ber.error.UnderRunError, why:
            raise asn1.UnderRun(why)

        except pysnmp.asn1.encoding.ber.error.BadEncodingError, why:
            raise asn1.BadEncoding(why)

        except pysnmp.asn1.encoding.ber.error.BerEncodingError, why:
            raise asn1.Error(why)

        # Catch asn1 package exceptions
        
        except pysnmp.asn1.error.BadArgumentError, why:
            raise asn1.BadArgument(why)

        except pysnmp.asn1.error.ValueConstraintError, why:
            raise asn1.TypeError(why)

        except pysnmp.asn1.error.Asn1Error, why:
            raise asn1.Error(why)

    def __str__(self):
        """Return native representation of instance payload
        """
        res = ''
        for key in self.keys():
            if res:
                res = res + ', ' + key + '=' + str(self[key])
            else:
                res = key + '=' + str(self[key])
        return self.__class__.__name__ + ': ' + res 

    def __repr__(self):
        """Return native representation of instance payload
        """
        res = ''
        for key in self.keys():
            if res:
                res = res + ', ' + key + '=' + repr(self[key])
            else:
                res = key + '=' + repr(self[key])
        return self.__class__.__name__ + '(' + res + ')'

    def __cmp__(self, other):
        """Compatibility comparation method
        """
        return self._wrapper_fun(self.__cmp_fun__, other)

    def __cmp_fun__(self, other):
        """Compare requests
        """
        if not isinstance(other, CompatBase):
            raise BadArgument('Can not compare %s vs %s' %
                              (str(self), str(other)))
                              
        if self['request_id'] == other['request_id']:
            return 0

        return -1

    def _decode_fun(self, data):
        """Call decode() by wrapper
        """
        return self.msg.decode(data)
    
    def decode(self, data):
        """Compatibility method: decode BER octet stream into this ASN.1 object
        """
        try:
            return self._wrapper_fun(self._decode_fun, data)

        except asn1.BadEncoding, why:
            raise BadEncoding(why)

        except asn1.UnknownTag, why:
            raise BadPDUType(why)

    def _encode_fun(self, kwdict):
        """Call encode() by wrapper
        """
        self.update(kwdict)
        return self.msg.encode()

    def encode(self, **kwargs):
        """Compatibility method: assign a value and encode
           it into BER octet stream
        """
        return self._wrapper_fun(self._encode_fun, kwargs)

    #
    # Dictionary interface
    #
    
    def _getitem_fun(self, key):
        """Return message item by key
        """
        if key == 'encoded_oids':
            return map(lambda x: x['name'].encode(), \
                       self.msg['pdu'].values()[0]['variable_bindings'])
        elif key == 'encoded_vals':
            return map(lambda x: x['value'].encode(), \
                       self.msg['pdu'].values()[0]['variable_bindings'])
        elif key == 'request_id' or key == 'error_status' or \
             key == 'error_index':
            return self.msg['pdu'].values()[0][key].get()
        elif key == 'community' or key == 'version':
            return self.msg[key].get()
        elif key == 'tag':
            return self.__class__.__name__

        raise KeyError('Non-applicible key: %s' % key)

    def __getitem__(self, key):
        """Call __getitem__ by wrapper
        """
        return self._wrapper_fun(self._getitem_fun, key)

    def _setitem_fun(self, key, value):
        """Set message item by key
        """
        if key == 'encoded_oids':
            # Decode OIDs
            oids = map(lambda x: v1.ObjectName(), value)
            map(lambda x, y: x.decode(y), oids, value)

            # Fetch vals
            vals = map(lambda x: x['value'], \
                       self.msg['pdu'].values()[0]['variable_bindings'])

            # Wild hack to keep OIDs & vals balanced
            if len(oids) > len(vals):
                vals.extend(map(lambda x: v1.ObjectSyntax(),
                                [ None ] * (len(oids) - len(vals))))

            # Re-commit OID-value pairs
            self.msg['pdu'].values()[0]['variable_bindings'] = apply(v1.VarBindList, map(lambda x, y: v1.VarBind(name=x, value=y), oids, vals))

        elif key == 'encoded_vals':
            # Fetch OIDs
            oids = map(lambda x: x['name'], \
                       self.msg['pdu'].values()[0]['variable_bindings'])

            # Decode vals
            vals = map(lambda x: v1.ObjectSyntax(), value)
            map(lambda x, y: x.decode(y), vals, value)

            # Wild hack to keep OIDs & vals balanced
            if len(oids) < len(vals):
                oids.extend(map(v1.ObjectName,
                                ['.1.3'] * (len(vals) - len(oids))))
            
            # Re-commit OID-value pairs
            self.msg['pdu'].values()[0]['variable_bindings'] = apply(v1.VarBindList, map(lambda x, y: v1.VarBind(name=x, value=y), oids, vals))

        elif key == 'request_id' or key == 'error_status' or \
             key == 'error_index':
            self.msg['pdu'].values()[0][key].set(value)
        elif key == 'community' or key == 'version':
            self.msg[key].set(value)
        elif key == 'tag':
            pass
        else:
            raise KeyError('Non-applicible key: %s' % key)
    
    def __setitem__(self, key, value):
        """Call __setitem__ by wrapper
        """
        return self._wrapper_fun(self._setitem_fun, key, value)

    def keys(self):
        """Return keys known to compatibility API
        """
        return [ 'encoded_oids', 'encoded_vals', 'request_id', 'error_status',
                 'error_index', 'tag', 'version', 'community' ]

    def has_key(self, key):
        """Return true if key exists in dictionary
        """
        return key in self.keys()

    def get(self, key, default):
        """Get values by key with default
        """
        if self.has_key(key):
            return self[key]

        return default

    def update(self, args):
        """Update dict with the other dict
        """
        for key in args.keys():
            self[key] = args[key]

    def clear(self):
        """Clear dict payload
        """
        self.msg = self.msgProto()

class _CompatRequest(CompatBase):
    """Base class for all request classes
    """
    def reply(self, **kwargs):
        """Build a response message from request message
        """
        rsp = GETRESPONSE(community=self['community'], \
                          request_id=self['request_id'], \
                          encoded_oids=self['encoded_oids'], \
                          encoded_vals=self['encoded_vals'])
        rsp.update(kwargs)
        return rsp
        
class GETREQUEST(_CompatRequest):
    """Compatibility interface to GETREQUEST
    """
    msgProto = v1.GetRequest

class GETNEXTREQUEST(_CompatRequest):
    """Compatibility interface to GETNEXTREQUEST
    """
    msgProto = v1.GetNextRequest

class SETREQUEST(_CompatRequest):
    """Compatibility interface to SETREQUEST
    """
    msgProto = v1.SetRequest

class GETRESPONSE(CompatBase):
    """Compatibility interface to GETRESPONSE
    """
    msgProto = v1.GetResponse

class TRAPREQUEST(CompatBase):
    """Compatibility interface to TRAPREQUEST
    """
    msgProto = v1.Trap

    #
    # Dictionary interface
    #
    
    def _getitem_fun(self, key):
        """Return message item by key
        """
        if key == 'generic_trap' or key == 'specific_trap' or \
           key == 'time_stamp' or key == 'enterprise':
            return self.msg['pdu'].values()[0][key].get()
        elif key == 'agent_address':
            return self.msg['pdu'].values()[0]['agent_addr']['internet'].get()
        else:
            return CompatBase._getitem_fun(self, key)

    def _setitem_fun(self, key, value):
        """Set message item by key
        """
        if key == 'generic_trap' or key == 'specific_trap' or \
           key == 'time_stamp' or key == 'enterprise':            
            self.msg['pdu'].values()[0][key].set(value)
        elif key == 'agent_address':
            self.msg['pdu'].values()[0]['agent_addr']['internet'].set(value)
        else:
            CompatBase._setitem_fun(self, key, value)

    def keys(self):
        """Return keys known to compatibility API
        """
        return [ 'encoded_oids', 'encoded_vals', 'generic_trap',
                 'specific_trap', 'agent_address', 'time_stamp',
                 'enterprise', 'tag', 'version', 'community' ]
    
def decode(data):
    """
       decode(input) -> (<request-object>, rest)

       Decode input octet stream (string) into a request-object and return
       the rest of input (string).
    """
    for msgType in [ GETREQUEST, GETNEXTREQUEST, SETREQUEST, GETRESPONSE,
                     TRAPREQUEST ]:
        msg = msgType()
        try:
            rest = msg.decode(data)

        except BadPDUType:
            continue
        
        return (msg, rest)
    
    raise BadPDUType('Unsuppored SNMP PDU type')
