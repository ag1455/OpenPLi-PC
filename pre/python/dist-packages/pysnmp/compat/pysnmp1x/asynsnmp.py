"""
   Deprecated PySNMP 1.x compatibility interface to asynchronous SNMP v.1
   engine implementation.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import asyncore
from pysnmp.compat.pysnmp1x import session, error

class async_session(asyncore.dispatcher, session.session):
    """An asynchronous SNMP engine based on the asyncore.py classes.

       Send SNMP requests and receive a responses asynchronously.
    """
    def __init__(self, agent, community,\
                  caller_fun, caller_data=None):
        # Make sure we get the callback function
        if not callable(caller_fun):
            raise error.BadArgument('Bad callback function')

        # Call parent classes constructors
        asyncore.dispatcher.__init__(self)
        session.session.__init__(self, agent, community)
                                 
        # Keep references to data and method objects supplied
        # by caller for callback on request completion.
        self.caller_data = caller_data
        self.caller_fun = caller_fun

    def open(self):
        """
           open()
           
           Create a socket and pass it to asyncore dispatcher.
        """
        asyncore.dispatcher.set_socket(self, session.session.open(self))

    def send_request(self, encoded_oids, encoded_vals, type='GETREQUEST'):
        """
           send_request(encoded_oids, encoded_vals[, type])
           
           Build and send SNMP message to remote SNMP process (as specified
           on async_session object creation) composed from encoded
           Object IDs along with their associated values.

           A callback function (as specified on async_session object creation)
           will be invoked on response arrival or request timeout.
        """
        self.request = session.session.encode_request(self, type, \
                                                      encoded_oids, \
                                                      encoded_vals)
        session.session.send(self, self.request)

    def handle_read(self):
        """Read SNMP reply from socket.

           This does NOT time out so one needs to implement a mean of
           handling timed out requests (perhaps it's worth looking at
           medusa/event_loop.py for an interesting approach).
        """
        (self.response, self.addr) = self.recvfrom(65536)

        try:
            # There seems to be no point in delivering pysnmp exceptions
            # from here as they would arrive out of context...
            (encoded_oids, encoded_vals) = \
                           session.session.decode_response(self, self.response)

        # Catch all known pysnmp exceptions and return a tuple of None's
        # as exceptions would then arrive out of context at this point.
        except error.PySNMPError:
            # Return a tuple of None's to indicate the failure
            (encoded_oids, encoded_vals) = (None, None)

        # Pass SNMP response along with references to caller specified data
        # and ourselves
        self.caller_fun(self, self.caller_data, encoded_oids, encoded_vals)

    def writable(self):
        """Objects of this class never expect write events
        """
        return 0

    def handle_connect(self):
        """Objects of this class never expect connect events
        """
        pass
