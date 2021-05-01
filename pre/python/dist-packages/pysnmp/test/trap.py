"""SNMP TRAP test"""
from pysnmp.proto.api import alpha
import base

class TrapV1AppTestCase(base.SnmpEntityTestCase):
    snmpProto = alpha.protoVersions[alpha.protoVersionId1]
    enterprise = '1.2.3.4.5'
    agentAddr = '127.0.0.1'
    genericTrap = 2
    specificTrap = 3
    timeStamp = 12345678
    oidVals = [
        ('.1.3.6.1.2.1.1.1.0', snmpProto.OctetString('testing')),
        ('.1.3.6.1.2.1.1.2.0', snmpProto.Integer(12345)),
        ('.1.3.6.1.2.1.1.3.0', snmpProto.IpAddress('127.0.0.1')) ]

    def agentCbFun(self, trapPdu):
        varBinds = map(lambda x: x.apiAlphaGetOidVal(), \
                       trapPdu.apiAlphaGetVarBindList())
        assert trapPdu.apiAlphaGetEnterprise() == self.enterprise, trapPdu
        assert trapPdu.apiAlphaGetAgentAddr() == self.agentAddr, trapPdu
        assert trapPdu.apiAlphaGetGenericTrap() == self.genericTrap, trapPdu
        assert trapPdu.apiAlphaGetSpecificTrap() == self.specificTrap, trapPdu
        assert trapPdu.apiAlphaGetTimeStamp() == self.timeStamp, trapPdu
        assert map(lambda (o, v): o, varBinds) == \
               map(lambda (o, v): o, self.oidVals)
    
    def testTrap(self):
        trapPdu = self.snmpProto.TrapPdu()
        trapPdu.apiAlphaSetEnterprise(self.enterprise)
        trapPdu.apiAlphaSetAgentAddr(self.agentAddr)
        trapPdu.apiAlphaSetGenericTrap(self.genericTrap)
        trapPdu.apiAlphaSetSpecificTrap(self.specificTrap)
        trapPdu.apiAlphaSetTimeStamp(self.timeStamp)
        apply(trapPdu.apiAlphaSetVarBindList, self.oidVals)
        self.managerSend(trapPdu)        
        self.agentInMsgs = 0
        while not self.agentInMsgs:
            self.dispatch()
    
class TrapV2cAppTestCase(base.SnmpEntityTestCase):
    snmpProto = alpha.protoVersions[alpha.protoVersionId2c]
    oidVals = [
        ('.1.3.6.1.2.1.1.1.0', snmpProto.Counter64(0x7fffffffffffffffl)),
        ('.1.3.6.1.2.1.1.2.0', snmpProto.Unsigned32(12345)),
        ('.1.3.6.1.2.1.1.3.0', snmpProto.IpAddress('127.0.0.1')) ]

    def agentCbFun(self, trapPdu):
        varBinds = map(lambda x: x.apiAlphaGetOidVal(), \
                       trapPdu.apiAlphaGetVarBindList())
        assert map(lambda (o, v): o, varBinds) == \
               map(lambda (o, v): o, self.oidVals), trapPdu
    
    def testTrap(self):
        trapPdu = self.snmpProto.TrapPdu()
        apply(trapPdu.apiAlphaSetVarBindList, self.oidVals)
        self.managerSend(trapPdu)
        self.agentInMsgs = 0
        while not self.agentInMsgs:
            self.dispatch()        

if __name__ == "__main__":
    base.unittest.main()
