"""
   Deprecated PySNMP 2.0.x compatibility interface to SNMP v.2c
   protocol implementation.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.proto import v2c
from pysnmp.compat.pysnmp2x import v1, asn1

class Error(v1.Error):
    """Base class for v2c module exceptions
    """
    pass

class BadArgument(Error):
    """Bad v2c object value
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

class CompatBase(v1.CompatBase):
    """Base class for compatibility classes
    """
    def _wrapper_fun(self, fun, *args):
        """Call passed function and translate possible exceptions
        """
        try:
            return apply(v1.CompatBase._wrapper_fun, [self, fun ] + list(args))

        except v1.BadPDUType, why:
            raise BadPDUType(why)

        except v1.BadVersion, why:
            raise BadVersion(why)

        except v1.BadEncoding, why:
            raise BadEncoding(why)

    def _setitem_fun(self, key, value):
        """Set message item by key
        """
        if key == 'encoded_oids':
            # Decode OIDs
            oids = map(lambda x: v2c.ObjectName(), value)
            map(lambda x, y: x.decode(y), oids, value)

            # Fetch vals
            vals = map(lambda x: x['value'].values()[0], \
                       self.msg['pdu'].values()[0]['variable_bindings'])

            # Wild hack to keep OIDs & vals balanced
            if len(oids) > len(vals):
                vals.extend(map(v2c.Null,
                                [ None ] * (len(oids) - len(vals))))

            # Re-commit OID-value pairs
            self.msg['pdu'].values()[0]['variable_bindings'] = apply(v2c.VarBindList, map(lambda x, y: v2c.VarBind(name=x, value=v2c.BindValue(value=y)), oids, vals))

        elif key == 'encoded_vals':
            # Fetch OIDs
            oids = map(lambda x: x['name'], \
                       self.msg['pdu'].values()[0]['variable_bindings'])

            # Decode vals
            vals = map(lambda x: v2c.BindValue(), value)
            map(lambda x, y: x.decode(y), vals, value)
            vals = map(lambda x: x.values()[0], vals)
            
            # Wild hack to keep OIDs & vals balanced
            if len(oids) < len(vals):
                oids.extend(map(v2c.ObjectName,
                                ['.1.3'] * (len(vals) - len(oids))))
            
            # Re-commit OID-value pairs
            self.msg['pdu'].values()[0]['variable_bindings'] = apply(v2c.VarBindList, map(lambda x, y: v2c.VarBind(name=x, value=v2c.BindValue(value=y)), oids, vals))
        else:
            v1.CompatBase._setitem_fun(self, key, value)

    def decode(self, data):
        """Compatibility method: decode BER octet stream into this ASN.1 object
        """
        try:
            return v1.CompatBase.decode(self, data)

        except v1.BadEncoding, why:
            raise BadEncoding(why)

        except v1.BadPDUType, why:
            raise BadPDUType(why)

class _CompatRequest(CompatBase):
    """Base class for all request classes
    """
    def reply(self, **kwargs):
        """Build a response message from request message
        """
        rsp = RESPONSE(community=self['community'], \
                       request_id=self['request_id'], \
                       encoded_oids=self['encoded_oids'], \
                       encoded_vals=self['encoded_vals'])
        rsp.update(kwargs)
        return rsp

class GETREQUEST(_CompatRequest):
    """Compatibility interface to GETREQUEST
    """
    msgProto = v2c.GetRequest

class GETNEXTREQUEST(_CompatRequest):
    """Compatibility interface to GETNEXTREQUEST
    """
    msgProto = v2c.GetNextRequest

class SETREQUEST(_CompatRequest):
    """Compatibility interface to SETREQUEST
    """
    msgProto = v2c.SetRequest

class TRAP(_CompatRequest):
    """Compatibility interface to TRAP message
    """
    msgProto = v2c.Trap

class INFORMREQUEST(_CompatRequest):
    """Compatibility interface to INFORMREQUEST
    """
    msgProto = v2c.InformRequest

class REPORT(_CompatRequest):
    """Compatibility interface to REPORT message
    """
    msgProto = v2c.Report

class RESPONSE(CompatBase):
    """Compatibility interface to RESPONSE message
    """
    msgProto = v2c.Response

# An alias to RESPONSE class
GETRESPONSE = RESPONSE

class GETBULKREQUEST(_CompatRequest):
    """Compatibility interface to GETBULKREQUEST
    """
    msgProto = v2c.GetBulkRequest
    
    #
    # Dictionary interface
    #
    
    def _getitem_fun(self, key):
        """Return message item by key
        """
        if key == 'non_repeaters' or \
           key == 'max_repetitions':
            return self.msg['pdu'].values()[0][key].get()
        else:
            return _CompatRequest._getitem_fun(self, key)

    def _setitem_fun(self, key, value):
        """Set message item by key
        """
        if key == 'non_repeaters' or \
           key == 'max_repetitions':
            return self.msg['pdu'].values()[0][key].set(value)
        else:
            return _CompatRequest._setitem_fun(self, key, value)

    def keys(self):
        """Return keys known to compatibility API
        """
        return [ 'encoded_oids', 'encoded_vals', 'request_id',
                 'non_repeaters', 'max_repetitions', 'tag', 'version',
                 'community' ]

def decode(data):
    """
       decode(input) -> (<request-object>, rest)

       Decode input octet stream (string) into a request-object and return
       the rest of input (string).
    """
    for msgType in [ GETREQUEST, GETNEXTREQUEST, SETREQUEST, RESPONSE,
                     INFORMREQUEST, TRAP, REPORT, GETBULKREQUEST]:
        msg = msgType()
        try:
            rest = msg.decode(data)

        except BadPDUType:
            continue

        except asn1.TypeError:
            break
        
        return (msg, rest)

    return v1.decode(data)
