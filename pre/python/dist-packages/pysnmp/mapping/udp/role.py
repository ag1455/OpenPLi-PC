"""
   Single-session, blocking network I/O classes.

   Copyright 1999-2004 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
import socket, select
from types import TupleType, ListType
from sys import stderr
from pysnmp.mapping.udp import error

class Manager:
    """Network client: send data item to server and receive a response
    """
    def __init__(self, agent=(None, 0), iface=('0.0.0.0', 0)):
        # Attempt to resolve default agent name
        host, port = agent
        if host is not None:
            try:
                host = socket.gethostbyname(host)
            except socket.error, why:
                raise error.NetworkError('gethostbyname() failed: %s' % why)
        self.agent = (host, port)

        # Initialize defaults
        self.iface = iface
        self.socket = None
        self.timeout = 1.0
        self.retries = 3

        # Defaults for flags
        self.dumpPacketsFlag = 0
        self.checkPeerAddrFlag = 0

    def __str__(self):
        return '%s session to %s from %s' % \
               (self.__class__.__name__, self.agent, self.iface)

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.agent, self.iface)
    
    def getSocket(self):
        """
           get_socket() -> socket

           Return socket object previously created with open() method.
        """
        return self.socket

    get_socket = getSocket

    def open(self):
        """
           open()
           
           Initialize transport layer (UDP socket) to be used
           for further communication with server.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        except socket.error, why:
            raise error.NetworkError('%s: socket() error: %s' %\
                                     (self.__class__.__name__, why))

        # Bind to specific interface on client machine
        try:
            self.socket.bind(self.iface)

        except socket.error, why:
            raise error.NetworkError('%s: bind() error: %s: %s' % \
                                     (self.__class__.__name__, \
                                      self.iface, why))
        return self.socket

    def send(self, request, dst=(None, 0)):
        """
           send(req[, dst])
           
           Send "req" message (string) to server by address specified on
           object creation or by "dst" address given in socket module 
           notation.
        """
        # Make sure the connection is established, open it otherwise
        if not self.socket:
            self.open()

        if dst == (None, 0): dst = self.agent

        try:
            self.socket.sendto(request, dst)
            
        except socket.error, why:
            raise error.NetworkError('%s: sendto() to %s error: %s' % \
                                     (self.__class__.__name__, dst, why))

        if self.dumpPacketsFlag: stderr.write('sent to %s: %s \n' %
                                              (dst, repr(request)))
        
    def read(self):
        """
           read() -> (message, src)
           
           Read data from the socket (assuming there's some data ready
           for reading), return a tuple of response message (as string)
           and source address 'src' (in socket module notation).
        """   
        # Make sure the connection exists
        if not self.socket:
            raise error.NetworkError('%s: socket not initialized' % \
                                     self.__class__.__name__)

        try:
            (message, src) = self.socket.recvfrom(65536)

        except socket.error, why:
            raise error.NetworkError('%s: recv() error: %s' % \
                                     (self.__class__.__name__, why))

        if self.dumpPacketsFlag: stderr.write('received from %s: %s\n' %
                                              (src, repr(message)))
        if self.checkPeerAddrFlag and self.agent != (None, 0):
            if src != self.agent and \
                   src != (socket.gethostbyname(self.agent[0]), self.agent[1]):
                raise error.NetworkError('%s: src/dst addresses mismatch: %s/%s' % (self.__class__.__name__, src, self.agent))
        return (message, src)
        
    def receive(self):
        """
           receive() -> (message, src)
           
           Wait for incoming data from network or timeout (and return
           a tuple of None's).

           Return a tuple of received data item (as string) and source address
           'src' (in socket module notation).
        """
        # Make sure the connection exists
        if not self.socket:
            raise error.NetworkError('%s: socket not initialized' % \
                                     self.__class__.__name__)

        # Wait for response
        r, w, x = select.select([self.socket], [], [], self.timeout)

        # Timeout occurred?
        if r:
            return self.read()

        # No answer, raise an exception
        raise error.NoResponseError('%s: no response arrived before timeout' %\
                                    self.__class__.__name__)

    def sendAndReceive(self, message, dst=(None, 0), cbFun=None):
        """
           sendAndEeceive(data[, dst, [(cbFun, cbCtx)]]) -> (data, src)
           
           Send data item to remote entity by address specified on object 
           creation or 'dst' address and receive a data item in response
           or timeout (and raise NoResponse exception).

           Return a tuple of data item (as string) and source address
           'src' (in socket module notation).
        """
        # Expand cbFun to cbFun&cbCtx preserving compatibility
        if type(cbFun) != TupleType:
            cbFun, cbCtx = (cbFun, None)
        else:
            cbFun, cbCtx = cbFun

        if cbFun is not None and not callable(cbFun):
            raise error.BadArgumentError('%s: non-callable callback function' %
                                         self.__class__.__name__)
        
        # Initialize retries counter
        retries = 0

        # Send request till response or retry counter hits the limit
        while retries < self.retries:
            # Send a request
            self.send(message, dst)

            # Wait for response
            while 1:
                try:
                    (response, src) = self.receive()

                except error.NoResponseError:
                    # Give it another try
                    break

                # Got some response
                if cbFun is None:
                    # Response is not verified
                    return (response, src)
                else:
                    if cbCtx is None:
                        # Compatibility aid                        
                        r = cbFun(response, src)
                    else:
                        r = cbFun(response, src, cbCtx)
                    # Response is good
                    if r:
                        return (response, src)
                    else:
                        continue

            # Otherwise, try it again
            retries = retries + 1

        # No answer, raise an exception
        raise error.NoResponseError('%s: no response arrived in %d secs * %d retries' % (self.__class__.__name__, self.timeout, self.retries))
    
    send_and_receive = sendAndReceive
    
    def close(self):
        """
           close()
           
           Terminate communication with remote server.
        """
        # See if it's opened
        if self.socket:
            try:
                self.socket.close()

            except socket.error, why:
                raise error.NetworkError('%s: close() error: %s' % \
                                         (self.__class__.__name__, why))

            # Initialize it to None to indicate it's closed
            self.socket = None  

# Compatibility alias
manager = Manager

class Agent:
    """Network client: receive requests, send back responses
    """
    def __init__(self, (cbFun, cbCtx)=(None, None),
                 ifaces=[('0.0.0.0', 161)]):
        # Block on select() waiting for request by default
        self.timeout = None

        if type(ifaces) != ListType:
            raise error.BadArgumentError('%s: interfaces list is not a list' %
                                         self.__class__.__name__)
        self.ifaces = ifaces
        self.socket = None

        # Store callback information
        self.cbFun = cbFun
        self.cbCtx = cbCtx

        self.dumpPacketsFlag = 0

    def __str__(self):
        return '%s listening at %s' % \
               (self.__class__.__name__, self.ifaces)

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, \
                               (self.cbFun, self.cbCtx), self.ifaces)
        
    def get_socket(self):
        """
           get_socket() -> socket

           Return socket object previously created with open() method.
        """
        return self.socket

    def open(self):
        """
           open()
           
           Initialize transport internals to be used for further
           communication with client.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        except socket.error, why:
            raise error.NetworkError('%s: socket() error: %s' % \
                                     (self.__class__.__name__, why))

        # Bind to specific interfaces at server machine
        for iface in self.ifaces:
            try:
                self.socket.bind(iface)

            except socket.error, why:
                raise error.NetworkError('%s: bind() error: %s: %s' % \
                                         (self.__class__.__name__, iface, why))

        return self.socket

    def send(self, message, dst):
        """
           send(rsp, dst)
           
           Send response message (given as string) to client process
           by 'dst' address given in socket module notation.
        """
        # Make sure the connection is established, open it otherwise
        if not self.socket:
            raise error.NetworkError('%s socket not initialized' % \
                                     self.__class__.__name__)
        
        try:
            self.socket.sendto(message, dst)
                
        except socket.error, why:
            raise error.NetworkError('%s: send() error: %s' % \
                                     (self.__class__.__name__, why))

        if self.dumpPacketsFlag: stderr.write('sent: %s\n' % repr(message))

    def read(self):
        """
           read() -> (req, src)
           
           Read data from the socket (assuming there's some data ready
           for reading), return a tuple of request (as string) and
           source address 'src' (in socket module notation).
        """   
        # Make sure the connection exists
        if not self.socket:
            raise error.NetworkError('%s: socket not initialized' %
                                     self.__class__.__name__)

        try:
            (message, peer) = self.socket.recvfrom(65536)

        except socket.error, why:
            raise error.NetworkError('%s: recvfrom() error: %s' % \
                                     (self.__class__.__name__, why))

        if self.dumpPacketsFlag: stderr.write('received: %s\n' % repr(message))
        
        return (message, peer)
        
    def receive(self):
        """
           receive() -> (req, src)
           
           Wait for and receive request message from remote process
           or timeout.

           Return a tuple of request message (as string) and source address
           'src' (in socket module notation).
        """
        # Attempt to initialize transport stuff
        if not self.socket:
            self.open()
            
        # Initialize sockets map
        r, w, x = [ self.socket ], [], []

        # Wait for response
        r, w, x = select.select(r, w, x, self.timeout)

        # Timeout occurred?
        if r:
            return self.read()

        raise error.IdleTimeoutError('%s: no request arrived before timeout' %
                                     self.__class__.__name__)
    
    def receiveAndSend(self, (cbFun, cbCtx)=(None, None)):
        """
           receive_and_send((cbFun, cbCtx))
           
           Wait for request from a client process or timeout (and raise
           IdleTimeoutError exception), pass request to the callback function
           to build a response, send response back to client process.
        """
        if cbFun is None:
            (cbFun, cbCtx) = (self.cbFun, self.cbCtx)
            
        if not callable(cbFun):
            raise error.BadArgumentError('%s: non-callable callback function' %
                                         self.__class__.__name__)

        while 1:
            # Wait for request to come
            (request, src) = self.receive()

            if not request:
                raise error.IdleTimeoutError('%s: no request arrived before timeout' % self.__class__.__name__)

            # Invoke callback function
            (response, dst) = cbFun(self, cbCtx, (request, src))

            # Send a response if any
            if response:
                # Reply back by either source address or alternative
                # destination whenever given
                if dst:
                    self.send(response, dst)
                else:
                    self.send(response, src)

    receive_and_send = receiveAndSend
    
    def close(self):
        """
           close()
           
           Close UDP socket used for communication with client.
        """
        # See if it's opened
        if self.socket:
            try:
                self.socket.close()

            except socket.error, why:
                raise error.NetworkError('%s: close() error: %s' %
                                         (self.__class__.__name__, why))

            # Initialize it to None to indicate it's closed
            self.socket = None  

# Compatibility alias
agent = Agent
