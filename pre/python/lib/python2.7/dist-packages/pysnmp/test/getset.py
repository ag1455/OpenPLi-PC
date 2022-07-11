"""SNMP GET test"""
from pysnmp.proto.api import alpha
import base

class GetSetAppMixIn:
    def agentCbFun(self, reqPdu):
        varBinds = map(lambda x: x.apiAlphaGetOidVal(), \
                       reqPdu.apiAlphaGetVarBindList())
        assert map(lambda (o, v): o, varBinds) == \
               map(lambda (o, v): o, self.oidVals), \
               (map(lambda (o, v): o, varBinds),
                map(lambda (o, v): o, self.oidVals))
        rspPdu = reqPdu.apiAlphaReply()
        apply(rspPdu.apiAlphaSetVarBindList, self.oidVals)
        return rspPdu
    
    def __testGetAndSet(self, reqPdu):
        def cbFun(rspPdu, self=self, reqPdu=reqPdu):
            if reqPdu.match(rspPdu):
                varBinds = map(lambda x: x.apiAlphaGetOidVal(), \
                               rspPdu.apiAlphaGetVarBindList())
                assert varBinds == self.oidVals, (varBinds, self.oidVals)
                self.__gotReply = 1
                return 1

        self.__gotReply = 0
        self.managerSendAndReceive(reqPdu, cbFun)
        assert self.__gotReply

    def testGet(self):
        reqPdu = self.snmpProto.GetRequestPdu()
        apply(reqPdu.apiAlphaSetVarBindList, \
              map(lambda (o, v): (o, None), self.oidVals))
        reqPdu.decode(reqPdu.encode())
        self.__testGetAndSet(reqPdu)

    def testSet(self):
        reqPdu = self.snmpProto.SetRequestPdu()
        apply(reqPdu.apiAlphaSetVarBindList, self.oidVals)
        self.__testGetAndSet(reqPdu)

class GetSetV1AppTestCase(base.SnmpEntityTestCase, GetSetAppMixIn):
    snmpProto = alpha.protoVersions[alpha.protoVersionId1]
    oidVals = [
        ('.1.3.6.1.2.1.1.1.1.0', snmpProto.Integer(0xffffffffL)),
        ('.1.3.6.1.2.1.1.1.2.0', snmpProto.Integer(-1)),
        ('.1.3.6.1.2.1.1.2.0', snmpProto.OctetString('oops')),
        ('.1.3.6.1.2.1.1.3.1.0', snmpProto.Null(0)),
        ('.1.3.6.1.2.1.1.3.2.0', snmpProto.Null('')),
        ('.1.3.6.1.2.1.1.3.3.0', snmpProto.Null()),
        ('.1.3.6.1.2.1.1.4.1.0', snmpProto.ObjectIdentifier('.1.3.6.5.4')),
        ('.1.3.6.1.2.1.1.4.2.0', snmpProto.ObjectIdentifier([1,3,6,5,4])),
        ('.1.3.6.1.2.1.1.5.0', snmpProto.IpAddress('127.0.0.1')),
        ('.1.3.6.1.2.1.1.6.0', snmpProto.Counter(123456)),
        ('.1.3.6.1.2.1.1.7.0', snmpProto.Gauge(654321)),
        ('.1.3.6.1.2.1.1.8.0', snmpProto.TimeTicks(0)),
        ('.1.3.6.1.2.1.1.9.0', snmpProto.Opaque('\000\001\002'))
    ]
    
class GetSetV2cAppTestCase(base.SnmpEntityTestCase, GetSetAppMixIn):
    snmpProto = alpha.protoVersions[alpha.protoVersionId2c]
    oidVals = [
        ('.1.3.6.1.2.1.1.1.1.0', snmpProto.Integer(0x7fffffff)),
        ('.1.3.6.1.2.1.1.1.2.0', snmpProto.Integer(-1)),
        ('.1.3.6.1.2.1.1.2.1.0', snmpProto.Integer32(1)),
        ('.1.3.6.1.2.1.1.2.2.0', snmpProto.Integer32(-1)),
        ('.1.3.6.1.2.1.1.3.0', snmpProto.OctetString('oops')),
        ('.1.3.6.1.2.1.1.4.0', snmpProto.BitString('1010101')),
        ('.1.3.6.1.2.1.1.5.1.0', snmpProto.Null('')),
        ('.1.3.6.1.2.1.1.5.2.0', snmpProto.Null(0)),
        ('.1.3.6.1.2.1.1.5.3.0', snmpProto.Null()),
        ('.1.3.6.1.2.1.1.6.1.0', snmpProto.ObjectIdentifier('.1.3.6.5.4')),
        ('.1.3.6.1.2.1.1.6.2.0', snmpProto.ObjectIdentifier([1,3,6,5,4])),
        ('.1.3.6.1.2.1.1.7.0', snmpProto.IpAddress('127.0.0.1')),
        ('.1.3.6.1.2.1.1.8.0', snmpProto.Counter32(123456)),
        ('.1.3.6.1.2.1.1.9.0', snmpProto.Gauge32(654321)),
        ('.1.3.6.1.2.1.1.10.0', snmpProto.Unsigned32(654321)),
        ('.1.3.6.1.2.1.1.11.0', snmpProto.TimeTicks(0)),
        ('.1.3.6.1.2.1.1.12.0', snmpProto.Opaque('\000\001\002')),
        ('.1.3.6.1.2.1.1.13.0', snmpProto.Counter64(0x7fffffffffffffffl))
    ]

if __name__ == "__main__":
    base.unittest.main()
