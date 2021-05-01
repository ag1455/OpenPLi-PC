"""
   Deprecated PySNMP 1.x compatibility interface to SNMP v.1 engine
   implementation.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.mapping.udp import role
from pysnmp.compat.pysnmp1x import message, error

class session(message.message):
    """Depricated PySNMP 1.x compatibility SNMP engine class. Build & send
       SNMP request, receive & parse SNMP response.
    """
    def _init_fun(self, agent, community='public'):
        """Compatibility constructor
        """
        message.message.__init__(self, community)

        # Initialize defaults
        self.agent = agent
        self.port = 161
        self.timeout = 1.0
        self.retries = 3
        self.iface = None

        # This is a provision for multisession superclass
        self.request = None
        self.response = None

        # Init socket transport
        self.open()

    def __init__(self, agent, community='public'):
        """Initialize session object
        """
        return self._wrapper(self._init_fun, agent, community)

    def _open_fun(self):
        """Compatibility method: create SNMP manager transport
        """
        self.mgr = role.manager()
        
        if self.iface is not None:
            self.mgr.iface = (self.iface[0], self.port)
        self.mgr.timeout = self.timeout
        self.mgr.retries = self.retries
        
        return self.mgr.open()
        
    def open(self):
        """
           open()

           Initialize transport layer (UDP socket) to be used
           for further communication with remote SNMP process.
        """
        return self._wrapper(self._open_fun)

    def store(self, request):
        """
           store(message)

           Store SNMP message for later transmission.
        """
        if not request:
            raise error.BadArgument('Empty SNMP message')        
        self.request = request

    def _get_socket_fun(self):
        """Compatibility method: return SNMP manager transport socket
        """
        return self.mgr.get_socket()

    def get_socket (self):
        """
           get_socket() -> socket
           
           Return socket object previously created with open() method.
        """
        return self._wrapper(self._get_socket_fun)

    def _send_fun(self, request=None):
        """Compatibility method: send request message
        """
        if request is None:
            if self.request is None:
                raise error.BadArgument('Empty SNMP message')
            else:
                self.mgr.send(self.request, (self.agent, self.port))
        else:
            self.mgr.send(request, (self.agent, self.port))

    def send(self, request=None):
        """
           send([message])

           Send SNMP message (the specified one or previously submitted
           with store() method) to remote SNMP process specified on
           session object creation.
        """
        return self._wrapper(self._send_fun)

    def _read_fun(self):
        """Compatibility method: read request from socket
        """
        return self.mgr.read()[0]

    def read(self):
        """
           read() -> message

           Read data from the socket (assuming there's some data ready
           for reading), return SNMP message (as string).
        """
        return self._wrapper(self._read_fun)

    def _receive_fun(self):
        """Compatibility method: receive request from socket
        """
        return self.mgr.receive()[0]

    def receive(self):
        """
           receive() -> message

           Receive SNMP message from remote SNMP process or timeout
           (and return None).
        """
        return self._wrapper(self._receive_fun)

    def _send_and_receive_fun(self, message):
        """Compatibility method: send request and receive reply
        """
        return self.mgr.send_and_receive(message, (self.agent, self.port))[0]

    def send_and_receive(self, message):
        """
           send_and_receive(message) -> message

           Send SNMP message to remote SNMP process (as specified on
           session object creation) and receive a response message
           or timeout (and raise NoResponse exception).
        """
        return self._wrapper(self._send_and_receive_fun, message)

    def _close_fun(self):
        """Compatibility method: close SNMP session
        """
        return self.mgr.close()

    def close(self):
        """
           close()

           Close UDP socket used to communicate with remote SNMP agent.
        """
        return self._wrapper(self._close_fun)
