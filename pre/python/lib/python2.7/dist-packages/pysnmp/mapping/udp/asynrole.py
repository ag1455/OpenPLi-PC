"""
   Asynchronous SNMP manager class based on Sam Rushing's asyncore class.

   Copyright 1999-2002 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from types import ClassType
import sys, asyncore
from pysnmp.mapping.udp import role, error
from pysnmp.error import PySnmpError

class Manager(asyncore.dispatcher):
    """An asynchronous SNMP manager based on the asyncore.py class.
    """
    def __init__(self, (cbFun, cbCtx)=(None, None), dstAddr=(None, 0), \
                 iface=('0.0.0.0', 0)):
        self.cbFun = cbFun; self.cbCtx = cbCtx

        asyncore.dispatcher.__init__(self)
        
        self.manager = role.Manager(dstAddr, iface)
        self.set_socket(self.manager.open())

    def send(self, reqMsg, dstAddr=(None, 0), (cbFun, cbCtx)=(None, None)):
        """
           send(reqMsg[, dstAddr[, (cbFun, cbCtx)]])
           
           Send SNMP message (string) to remote server process as specified
           on manager object creation or by 'dstAddr' address (given
           in socket module notation).

           The callback function (as specified on manager object creation)
           will be invoked on response arrival or error.
        """
        if cbFun is not None:
            self.cbFun = cbFun
        if cbCtx is not None:
            self.cbCtx = cbCtx
            
        self.manager.send(reqMsg, dstAddr)

    def handle_read(self):
        """Overloaded asyncore method -- read SNMP reply message from
           socket.        

           This does NOT time out so one needs to implement a mean of
           handling timed out requests (see examples/async_snmp.py for
           one of possible solutions).
        """
        (rspMsg, srcAddr) = self.manager.read()

        # Pass SNMP response along with references to caller specified data
        # and ourselves
        self.cbFun(self, self.cbCtx, (rspMsg, srcAddr), (None, None, None))

    def writable(self):
        """Objects of this class never expect write events
        """
        return 0

    def handle_connect(self):
        """Objects of this class never expect connect events
        """
        pass

    def handle_close(self):
        """Invoked by asyncore on connection closed event
        """
        self.manager.close()

    def handle_error(self, excType=None, excValue=None, excTraceback=None):
        """Invoked by asyncore on any exception
        """
        # In modern Python distribution, the handle_error() does not receive
        # exception details
        if excType is None or excValue is None or excTraceback is None:
            excType, excValue, excTraceback = sys.exc_info()
            
        # In case of PySNMP exception, invoke the callback function
        # and pass it an empty result. Otherwise,just pass the exception on.
        if type(excType) == ClassType and \
           issubclass(excType, PySnmpError):
            self.cbFun(self, self.cbCtx,\
                        (None, None), (excType, excValue, excTraceback))
        else:
            raise

# Compatibility alias
manager = Manager
    
class Agent(asyncore.dispatcher):
    """An asynchronous SNMP agent based on the asyncore.py class.

       Wait for and receive SNMP request messages, send SNMP response
       messages asynchronously.
    """
    def __init__(self, (cbFun, cbCtx), ifaces=[('0.0.0.0', 161)]):
        # Make sure we get the callback function
        if not callable(cbFun):
            raise error.BadArgumentError('Non-callable callback function')

        self.cbFun = cbFun; self.cbCtx = cbCtx

        asyncore.dispatcher.__init__(self)
        self.agent = role.Agent((None, None), ifaces)
        self.set_socket(self.agent.open())

    def send(self, rspMsg, dstAddr):
        """
           send(rspMsg, dstAddr)
           
           Send SNMP message (string) to remote SNMP process by 'dstAddr' address
           (given in socket module notation).
        """
        self.agent.send(rspMsg, dstAddr)

    def handle_read(self):
        """Overloaded asyncore method -- read SNMP message from socket.

           This does NOT time out so one needs to implement a mean of
           handling timed out requests (perhaps it's worth looking at
           medusa/event_loop.py for an interesting approach).
        """
        reqMsg, srcAddr = self.agent.read()

        # Pass SNMP request along with references to caller specified data
        # and ourselves
        self.cbFun(self, self.cbCtx, (reqMsg, srcAddr), (None, None, None))

    def writable(self):
        """Objects of this class never expect write events
        """
        return 0

    def handle_connect(self):
        """Objects of this class never expect connect events
        """
        pass

    def handle_close(self):
        """Invoked by asyncore on connection closed event
        """
        self.agent.close()

    def handle_error(self, excType=None, excValue=None, excTraceback=None):
        """Invoked by asyncore on any exception
        """
        # In modern Python distribution, the handle_error() does not receive
        # exception details
        if excType is None or excValue is None or excTraceback is None:
            excType, excValue, excTraceback = sys.exc_info()

        # In case of PySNMP exception, invoke the callback function
        # and pass it an empty result. Otherwise,just pass the exception on.
        if type(excType) == ClassType \
           and issubclass(excType, PySnmpError):
            self.cbFun(self, self.cbCtx,
                        (None, None), (excType, excValue, excTraceback))
        else:    
            raise

# Compatibility alias
agent = Agent
