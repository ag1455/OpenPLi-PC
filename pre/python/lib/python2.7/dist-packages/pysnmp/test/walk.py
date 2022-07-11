"""SNMP GETNEXT/GETBULK tests"""
from pysnmp.proto.api import alpha
import base

class GetNextAppMixIn:
    def agentCbFun(self, reqPdu):
        varBinds = map(lambda x: x.apiAlphaGetOidVal(), \
                       reqPdu.apiAlphaGetVarBindList())
        rspPdu = reqPdu.apiAlphaReply()
        rspVarBinds = []; errorIndex = -1
        for oid, val in map(lambda x: x.apiAlphaGetOidVal(),
                            reqPdu.apiAlphaGetVarBindList()):
            mibIdx = -1; errorIndex = errorIndex + 1
            for idx in range(len(self.agtOidVals)):
                if idx == 0:
                    if oid < self.agtOidVals[idx][0]:
                        mibIdx = idx
                        break
                else:
                    if self.agtOidVals[idx][0] > oid >= \
                       self.agtOidVals[idx-1][0]:
                        mibIdx = idx
                        break
            else:
                apply(rspPdu.apiAlphaSetVarBindList, varBinds)
                rspPdu.apiAlphaSetEndOfMibIndices(errorIndex)
                return rspPdu
            
            if mibIdx != -1: rspVarBinds.append(self.agtOidVals[mibIdx])

        apply(rspPdu.apiAlphaSetVarBindList, rspVarBinds)
        return rspPdu
    
    def testGetNext(self):
        self.__EOM = 0
        reqPdu = self.snmpProto.GetNextRequestPdu()

        def cbFun(rspPdu, self=self, reqPdu=reqPdu):
            if reqPdu.match(rspPdu):
                self.__gotReply = 1
                tblIndices =  apply(
                    reqPdu.apiAlphaGetTableIndices, [ rspPdu ] \
                    + map(lambda (o, v): o, self.mgrOidVals)
                    )
                for idx in filter(lambda x: x==-1, tblIndices[-1]):
                    del self.mgrOidVals[idx]
                if len(self.mgrOidVals) == 0:
                    self.__EOM = 1
                    return 1
                apply(reqPdu.apiAlphaSetVarBindList, \
                      map(lambda (o, v): (o.get(), None), \
                          map(lambda cellIdx, \
                              varBindList=rspPdu.apiAlphaGetVarBindList(): \
                              varBindList[cellIdx].apiAlphaGetOidVal(), \
                              filter(lambda x: x!=-1, tblIndices[-1]))))
                reqPdu.apiAlphaGetRequestId().inc(1)
                return 1

        apply(reqPdu.apiAlphaSetVarBindList, \
              map(lambda (o, v): (o.get(), None), self.mgrOidVals))
        while not self.__EOM:
            self.__gotReply = 0
            self.managerSendAndReceive(reqPdu, cbFun)
            assert self.__gotReply

class GetNextV1AppTestCase(base.SnmpEntityTestCase, GetNextAppMixIn):
    snmpProto = alpha.protoVersions[alpha.protoVersionId1]
    agtOidVals = [
        (snmpProto.ObjectName('.1.3.6.1.2.1.1.1.0'),\
         snmpProto.OctetString('testing')),
        (snmpProto.ObjectName('.1.3.6.1.2.1.1.2.0'),\
         snmpProto.Integer(12345)),
        (snmpProto.ObjectName('.1.3.6.1.2.1.1.3.0'),\
         snmpProto.IpAddress('127.0.0.1')) ]
    mgrOidVals = [ (snmpProto.ObjectName('.1.3.6.1.2.1.1'), None),
                   (snmpProto.ObjectName('.1.3.6.1.2.1.2'), None) ]

class GetNextV2cAppTestCase(base.SnmpEntityTestCase, GetNextAppMixIn):
    snmpProto = alpha.protoVersions[alpha.protoVersionId2c]
    agtOidVals = [
        (snmpProto.ObjectName('.1.3.6.1.2.1.1.1.0'),\
         snmpProto.Counter64(0x7fffffffffffffffl)),
        (snmpProto.ObjectName('.1.3.6.1.2.1.1.2.0'),\
         snmpProto.Unsigned32(12345)),
        (snmpProto.ObjectName('.1.3.6.1.2.1.1.3.0'),\
         snmpProto.IpAddress('127.0.0.1')) ]
    mgrOidVals = [ (snmpProto.ObjectName('.1.3.6.1.2.1.1'), None),
                   (snmpProto.ObjectName('.1.3.6.1.2.1.2'), None) ]
        
if __name__ == "__main__":
    base.unittest.main()
