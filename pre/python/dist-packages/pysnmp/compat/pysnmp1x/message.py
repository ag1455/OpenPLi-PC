"""
   Deprecated PySNMP 1.x compatibility interface to SNMP v.1
   protocol implementation.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.proto import rfc1155, rfc1157
from pysnmp.compat.pysnmp1x import ber, error

class message(ber.ber):
    """Depricated PySNMP 1.x compatibility SNMP message processing class
    """
    def __init__ (self, community='public', version=0):
        """Compatibility constructor
        """
        self.community = community
        self.version = version
        self.request_id = 0
        
    def _encode_bindings_fun(self, encoded_oids, encoded_vals):
        """BER encode oids & values
        """
        # Decode OIDs
        oids = map(lambda x: rfc1155.ObjectName(), encoded_oids)
        map(lambda x, y: x.decode(y), oids, encoded_oids)

        # Decode vals
        vals = map(lambda x: rfc1155.ObjectSyntax(), encoded_vals)
        map(lambda x, y: x.decode(y), vals, encoded_vals)

        # Set defaults for missing vars
        if len(oids) > len(vals):
            vals.extend(map(lambda x: rfc1155.ObjectSyntax(),
                            [ None ] * (len(oids) - len(vals))))

        # Encode bindings
        return apply(rfc1157.VarBindList, \
                     map(lambda x, y: rfc1157.VarBind(name=x, value=y), \
                         oids, vals)).encode()

    def encode_bindings(self, encoded_oids, encoded_vals):
        """Compatibility method: BER encode oids & values
        """
        return self._wrapper(self._encode_bindings_fun, \
                             encoded_oids, encoded_vals)

    def _decode_bindings_fun(self, octetString):
        """BER decode bindings up to oids & values
        """
        # Decode bindings
        varBindList = rfc1157.VarBindList()
        varBindList.decode(octetString)

        # Build encoded_oids and encoded_vals
        encoded_oids = map(lambda x: x['name'].encode(), varBindList)
        encoded_vals = map(lambda x: x['value'].encode(), varBindList)

        return (encoded_oids, encoded_vals)

    def decode_bindings(self, octetString):
        """Compatibility method: BER decode bindings up to oids & values
        """
        return self._wrapper(self._decode_bindings_fun, octetString)

    def _encode_snmp_pdu_fun(self, pduType, bindings):
        """BER encode SNMP PDU
        """
        # Decode bindings
        varBindList = rfc1157.VarBindList()
        varBindList.decode(bindings)

        if pduType == 'GETREQUEST':
            pdu = rfc1157.GetRequestPdu()
        elif pduType == 'SETREQUEST':
            pdu = rfc1157.SetRequestPdu()
        elif pduType == 'GETNEXTREQUEST':            
            pdu = rfc1157.GetNextRequestPdu()
        elif pduType == 'GETRESPONSE':            
            pdu = rfc1157.GetResponsePdu()
        else:
            raise error.BadPDUType('Unrecognized PDU: %s' % pduType)

        pdu['variable_bindings'] = varBindList
        
        return pdu.encode()
    
    def encode_snmp_pdu(self, pduType, bindings):
        """Compatibility method: BER encode SNMP PDU
        """
        return self._wrapper(self._encode_snmp_pdu_fun, \
                             pduType, bindings)

    def _decode_snmp_pdu_fun(self, octetString):
        """BER decode SNMP PDU
        """
        # Decode pdu
        pdu = rfc1157.Pdus()
        pdu.decode(octetString)
        pdu = pdu.values()[0]

        return (pdu.tagId, pdu['request_id'].get(), pdu['error_status'].get(),
                pdu['error_index'].get(), pdu['variable_bindings'].encode())
                
    def decode_snmp_pdu(self, octetString):
        """Compatibility method: BER decode SNMP PDU
        """
        return self._wrapper(self._decode_snmp_pdu_fun, octetString)

    def _encode_request_sequence_fun(self, pdu):
        """BER encode SNMP request sequence
        """
        # Decode pdu
        requestPdu = rfc1157.Pdus()
        requestPdu.decode(pdu)

        # Create SNMP message and attach PDU
        msg = rfc1157.Message(pdu=requestPdu)

        # Update message options
        msg['version'].set(self.version)
        msg['community'].set(self.community)
        
        return msg.encode()
    
    def encode_request_sequence(self, pdu):
        """Compatibility method: BER encode SNMP request sequence
        """
        return self._wrapper(self._encode_request_sequence_fun, pdu)

    def _decode_response_sequence_fun(self, octetStream):
        """BER decode SNMP response sequence
        """
        # Create and decode SNMP message
        msg = rfc1157.Message()
        msg.decode(octetStream)

        return (msg['version'].get(), msg['community'].get(),
                msg['pdu'].encode())
    
    def decode_response_sequence(self, octetStream):
        """Compatibility method: BER decode SNMP response sequence
        """
        return self._wrapper(self._decode_response_sequence_fun,
                             octetStream)

    def _encode_request_fun(self, pduType, encoded_oids, encoded_vals):
        """Compatibility method: BER encode SNMP request message
        """
        # Decode OIDs
        oids = map(lambda x: rfc1155.ObjectName(), encoded_oids)
        map(lambda x, y: x.decode(y), oids, encoded_oids)

        # Decode vals
        vals = map(lambda x: rfc1155.ObjectSyntax(), encoded_vals)
        map(lambda x, y: x.decode(y), vals, encoded_vals)

        # Set defaults for missing vars
        if len(oids) > len(vals):
            vals.extend(map(lambda x: rfc1155.ObjectSyntax(),
                            [ None ] * (len(oids) - len(vals))))

        if pduType == 'GETREQUEST':
            pdu = rfc1157.GetRequestPdu()
        elif pduType == 'SETREQUEST':
            pdu = rfc1157.SetRequestPdu()
        elif pduType == 'GETNEXTREQUEST':            
            pdu = rfc1157.GetNextRequestPdu()
        else:
            raise error.BadPDUType('Unrecognized request type: %s' % pduType)

        # Store request ID for later verification
        self.request_id = pdu['request_id']
        
        # Attach bindings
        pdu['variable_bindings'] = apply(rfc1157.VarBindList, \
                                         map(lambda x, y: \
                                             rfc1157.VarBind(name=x, value=y),\
                                             oids, vals))

        # Create a message
        req = rfc1157.Message(pdu=rfc1157.Pdus(somepdu=pdu))

        # Update message options
        req['version'].set(self.version)
        req['community'].set(self.community)
        
        return req.encode()
    
    def encode_request(self, pduType, encoded_oids, encoded_values):
        """
           encode_request(type, encoded_oids, encoded_values) -> SNMP message
           
           Encode Object IDs and values (lists of strings) into variables
           bindings, then encode bindings into SNMP PDU (of specified type
           (string)), then encode SNMP PDU into SNMP message.
        """
        return self._wrapper(self._encode_request_fun, \
                             pduType, encoded_oids, encoded_values)

    def _decode_response_fun(self, octetStream, mtype):
        """Compatibility method: BER decode SNMP response message
        """
        if not octetStream:
            raise error.EmptyResponse('Empty SNMP message')
        
        # Create and decode SNMP message
        rsp = rfc1157.Message()
        rsp.decode(octetStream)

        # Check response validness
        if rsp['version'].get() != self.version:
            raise error.BadVersion('Unmatched SNMP versions: %d/%d' %
                                   (rsp['version'].get(), self.version))
        if rsp['community'].get() != self.community:
            raise error.BadCommunity('Unmatched SNMP community names: %s/%s' \
                                     % (rsp['community'].get(),self.community))

        # Retain curios check %-/
        if mtype == 'GETRESPONSE' and rsp['pdu'].has_key('get_response'):
            pass
        elif mtype == 'GETREQUEST' and rsp['pdu'].has_key('get_request'):
            pass
        elif mtype == 'SETREQUEST' and rsp['pdu'].has_key('set_request'):
            pass
        elif mtype == 'GETNEXTREQUEST' and \
             rsp['pdu'].has_key('get_next_request'):
            pass
        else:
            raise error.BadPDUType('Unexpected PDU type %s/%s' %
                                   (rsp['pdu'].keys()[0], mtype))

        # Handle SNMP errors
        pdu = rsp['pdu'].values()[0]
        if pdu['error_status']:
            raise error.SNMPError(pdu['error_status'].get(),\
                                  pdu['error_index'].get())

        # Make sure request ID's matched
        if pdu['request_id'] != self.request_id:
            raise error.BadRequestID ('Unmatched request/response IDs: %d/%d'\
                                      % (pdu['request_id'], self.request_id))

        # Build encoded_oids and encoded_vals
        encoded_oids = map(lambda x: x['name'].encode(), pdu['variable_bindings'])
        encoded_vals = map(lambda x: x['value'].encode(), pdu['variable_bindings'])

        return (encoded_oids, encoded_vals)

    def decode_response(self, message, mtype='GETRESPONSE'):
        """
           decode_response(message[, type]) -> (encoded_oids, encoded_values)
           
           Decode SNMP message (string) of specified type (default is
           'GETRESPONSE'), return lists of encoded Object IDs and their
           values (lists of strings).
        """
        return self._wrapper(self._decode_response_fun, message, mtype)

    # Trap stuff
    
    def _encode_snmp_trap_pdu_fun(self, enterprise, address, generic, \
                                   specific, timeticks, bindings):
        """BER encode SNMP TRAP PDU
        """
        # Decode bindings
        varBindList = rfc1157.VarBindList()
        varBindList.decode(bindings)

        # Create PDU and attach bindings
        pdu = rfc1157.TrapPdu(variable_bindings=varBindList)

        # Load options
        pdu['enterprise'].set(enterprise)
        pdu['agent_addr']['internet'].set(address)
        pdu['generic_trap'].set(generic)
        pdu['specific_trap'].set(specific)
        pdu['time_stamp'].set(timeticks)
        
        return pdu.encode()

    def encode_snmp_trap_pdu(self, enterprise, address, generic,
                             specific, timeticks, bindings):
        """Compatibility method: BER encode SNMP TRAP PDU
        """
        return self._wrapper(self._encode_snmp_trap_pdu_fun, enterprise,\
                             address, generic, specific, timeticks,\
                             bindings)

    def _decode_snmp_trap_pdu_fun(self, octetString):
        """BER decode SNMP TRAP PDU
        """
        # Decode pdu
        pdu = rfc1157.TrapPdu()
        pdu.decode(octetString)

        return (pdu.tagId, pdu['enterprise'].get(), \
                pdu['agent_addr']['internet'].get(), \
                pdu['generic_trap'].get(), pdu['specific_trap'].get(), \
                pdu['time_stamp'].get(), \
                pdu['variable_bindings'].encode())
                
    def decode_snmp_trap_pdu(self, octetString):
        """Compatibility method: BER decode SNMP TRAP PDU
        """
        return self._wrapper(self._decode_snmp_trap_pdu_fun, octetString)

    def _encode_trap_fun(self, enterprise, address, generic, specific,\
                         timeticks, encoded_oids, encoded_vals):
        """Compatibility method: BER encode SNMP TRAP message
        """
        # Decode OIDs
        oids = map(lambda x: rfc1155.ObjectName(), encoded_oids)
        map(lambda x, y: x.decode(y), oids, encoded_oids)

        # Decode vals
        vals = map(lambda x: rfc1155.ObjectSyntax(), encoded_vals)
        map(lambda x, y: x.decode(y), vals, encoded_vals)

        # Set defaults for missing vars
        if len(oids) > len(vals):
            vals.extend(map(lambda x: rfc1155.ObjectSyntax(),
                            [ None ] * (len(oids) - len(vals))))

        pdu = rfc1157.TrapPdu()

        # Load trap options
        pdu['enterprise'].set(enterprise)
        pdu['agent_addr']['internet'].set(address)
        pdu['generic_trap'].set(generic)
        pdu['specific_trap'].set(specific)
        pdu['time_stamp'].set(timeticks)
        
        # Attach bindings
        pdu['variable_bindings'] = apply(rfc1157.VarBindList,\
                                         map(lambda x, y: \
                                             rfc1157.VarBind(name=x, value=y),\
                                             oids, vals))

        # Create a message
        req = rfc1157.Message(pdu=rfc1157.Pdus(somepdu=pdu))

        # Update message options
        req['version'].set(self.version)
        req['community'].set(self.community)
        
        return req.encode()

    def encode_trap(self, enterprise, address, generic, specific,\
                    timeticks, encoded_oids=[], encoded_vals=[]):
        """
           encode_trap(type, encoded_oids, encoded_values) -> SNMP message
           
           Encode Object IDs and values (lists of strings) into variables
           bindings, then encode bindings into SNMP PDU (of specified type
           (string)), then encode SNMP PDU into SNMP message.
        """
        return self._wrapper(self._encode_trap_fun, enterprise, address, \
                             generic, specific, timeticks, encoded_oids, \
                             encoded_vals)

    def _decode_trap_fun(self, octetStream):
        """Compatibility method: BER decode SNMP TRAP message
        """
        if not octetStream:
            raise error.EmptyResponse('Empty SNMP message')
        
        # Create and decode SNMP message
        req = rfc1157.Message()
        req.decode(octetStream)

        # Check response validness
        if req['version'].get() != self.version:
            raise error.BadVersion('Unmatched SNMP versions: %d/%d' %
                                   (req['version'].get(), self.version))
        if req['community'].get() != self.community:
            raise error.BadCommunity('Unmatched SNMP community names: %s/%s' \
                                     % (req['community'].get(),self.community))

        if not req['pdu'].has_key('trap'):
            raise error.BadPDUType('Unexpected PDU type %s' % req['pdu'].keys()[0])

        # Build encoded_oids and encoded_vals
        encoded_oids = map(lambda x: x['name'].encode(), req['pdu'].values()[0]['variable_bindings'])
        encoded_vals = map(lambda x: x['value'].encode(), req['pdu'].values()[0]['variable_bindings'])

        return (req['pdu'].values()[0]['enterprise'].get(),
                req['pdu'].values()[0]['agent_addr']['internet'].get(),
                req['pdu'].values()[0]['generic_trap'].get(),
                req['pdu'].values()[0]['specific_trap'].get(),
                req['pdu'].values()[0]['time_stamp'].get(),
                encoded_oids, encoded_vals)

    def decode_trap(self, octetStream):
        """
           decode_trap(message) -> (enterprise, address, generic,
                                    specific, timeticks, encoded_oids,
                                     encoded_vals)
           
           Decode SNMP TRAP message (string).
        """
        return self._wrapper(self._decode_trap_fun, octetStream)
