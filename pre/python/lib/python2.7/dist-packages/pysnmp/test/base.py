"""Base class for SNMP entity testing"""
import asyncore
from pysnmp.proto.api import alpha
from pysnmp.mapping.udp import asynrole
from pysnmp.error import PySnmpError

class PySnmpTestError(PySnmpError): pass

try:
    import unittest
except ImportError:
    raise PySnmpTestError('PyUnit package\'s missing. See http://pyunit.sourceforge.net/')

class SnmpEntityTestCase(unittest.TestCase):
    """SNMP manager and agent within a single entity"""
    communityName = 'mycommunity'
    def setUp(self):
        for port in range(20000,25000):
            try:
                self.agent = asynrole.Agent((self.__agentCbFun, None), \
                                            [('127.0.0.1', port)])
            except PySnmpError:
                continue
            self.agentInMsgs = 0
            self.manager = asynrole.Manager((None, None), ('127.0.0.1', port))
            return

        raise PySnmpTestError('Cannot bind to any local port within a huge range')
    
    def tearDown(self):
        self.agent.close()
        self.manager.close()
        self.agent = self.manager = None

    def __agentCbFun(self, tsp, cbCtx, (oStream, srcAddr), (t, v, tb)):
        assert not t, (t, v, tb)
        self.agentInMsgs = self.agentInMsgs + 1
        f = getattr(self, 'agentCbFun', None)
        if f is not None:
            metaMsg = alpha.MetaMessage(); metaMsg.berDecode(oStream)
            reqMsg = metaMsg.apiAlphaGetCurrentComponent()
            assert reqMsg.apiAlphaGetCommunity() == self.communityName
            rspPdu = f(reqMsg.apiAlphaGetPdu())
            if rspPdu is not None:
                rspMsg = reqMsg.apiAlphaReply()
                rspMsg.apiAlphaSetPdu(rspPdu)
                self.agent.send(rspMsg.berEncode(), srcAddr)
        
    def __managerCbFun(self, tsp, cbFun, (oStream, srcAddr), (t, v, tb)):
        assert not t, (t, v, tb)
        rspMsg = self.snmpProto.Message(); rspMsg.berDecode(oStream)
        assert rspMsg.apiAlphaGetCommunity() == self.communityName
        rspPdu = rspMsg.apiAlphaGetPdu()
        if cbFun(rspPdu):
            self.__runFlag = 0

    def managerSend(self, reqPdu, cbFun=None):
        reqMsg = self.snmpProto.Message()
        reqMsg.apiAlphaSetCommunity(self.communityName)
        reqMsg.apiAlphaSetPdu(reqPdu)
        self.manager.send(reqMsg.berEncode(), (None, 0), \
                          (self.__managerCbFun, cbFun))

    def managerSendAndReceive(self, reqPdu, cbFun=None):
        self.managerSend(reqPdu, cbFun)
        self.__runFlag = 5
        while self.__runFlag:
            self.__runFlag = self.__runFlag - 1
            self.dispatch()
        
    def dispatch(self, timeout=1): asyncore.poll(timeout)

