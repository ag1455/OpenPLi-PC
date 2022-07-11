"""
   Deprecated PySNMP 1.x compatibility interface to multisession SNMP v.1
   engine implementation.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.mapping.udp import bulkrole
from pysnmp.compat.pysnmp1x import session, message, error

class multisession(message.message):
    """Depricated PySNMP 1.x compatibility multisession SNMP engine class.
       Build & send SNMP requests, receive & parse SNMP response.
    """
    def _init_fun(self):
        """Compatibility constructor
        """
        # Initialize defaults
        self.port = 161
        self.timeout = 1.0
        self.retries = 3
        self.iface = None

        self.initialize()
        
    def __init__(self):
        """Initialize class instance
        """
        return self._wrapper(self._init_fun)

    def _initialize_fun(self):
        """Compatibility method: reset private vars
        """
        if self.iface is None:
            self.mgr = bulkrole.manager()
        else:
            self.mgr = bulkrole.manager((self.iface[0], self.port))

        # Pass bulkmanager some options
        self.mgr.timeout = self.timeout
        self.mgr.retries = self.retries
        
    def initialize(self):
        """Reset private class instance variables to get ready
        """
        return self._wrapper(self._initialize_fun)

    def _submit_request_fun(self, agent, community, pduType, \
                            encoded_oids=[], encoded_vals=[]):
        """Compatibility method for submit_request()
        """
        # Create SNMP session
        ses = session.session(agent, community)
        question = ses.encode_request(pduType, encoded_oids, encoded_vals)

        # Submit question to bulkrole manager
        self.mgr.append(((agent, self.port), question, ses))
        
    def submit_request(self, agent, community='public',\
                       pduType='GETREQUEST',\
                       encoded_oids=[], encoded_vals=[]):
        """
           submit_request(agent[, community[, type[,\
                          encoded_oids[, encoded_vals]]]]):
        
           Create SNMP message of specified "type" (default is GETREQUEST)
           to be sent to "agent" with SNMP community name "community"
           (default is public) and loaded with encoded Object IDs
           "encoded_oids" along with their associated values "encoded_values"
           (default is empty lists).

           New SNMP message will be added to a queue of SNMP requests to
           be transmitted to their destinations (see dispatch()).
        """
        return self._wrapper(self._submit_request_fun, agent, community,
                             pduType, encoded_oids, encoded_vals)

    def _dispatch_fun(self):
        """Compatibility method for dispatch()
        """
        return self.mgr.dispatch()

    def dispatch(self):
        """
           dispatch()
           
           Send pending SNMP requests and receive replies (or timeout).
        """
        return self._wrapper(self._dispatch_fun)

    def _retrieve_fun(self):
        """Compatibility method for retrieve()
        """
        results = []
        for (dst, answer, ses) in self.mgr:
            encoded_pairs = ([], [])
            if answer:
                try:
                    encoded_pairs = ses.decode_response(answer)

                except error.SNMPError:
                    # SNMP errors lead to empty responses
                    pass
                
            results.append(encoded_pairs)
        
        return results
    
    def retrieve(self):
        """
           retrieve() -> [(encoded_oids, encoded_vals), ...]
           
           Retrieve previously received SNMP repsponses as a list of pairs
           of encoded Object IDs along with their associated values
           (unsuccessful, timed out requests will return a tuple of
           empty lists).

           The order of responses in the list is guaranteed to be the same
           as requests SNMP requests were submitted (see submit_request()).
        """
        return self._wrapper(self._retrieve)
