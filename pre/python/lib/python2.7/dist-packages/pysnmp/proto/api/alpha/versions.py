from pysnmp.proto import rfc1155, rfc1157, rfc1902, rfc1905

# Mix-in's
class ProtoVersionIdMixInBase:
    def apiAlphaGetProtoVersionId(self): return self.apiAlphaProtoVersionId

class ProtoVersionId1MixIn(ProtoVersionIdMixInBase):
    apiAlphaProtoVersionId = rfc1157.Version().get()

class ProtoVersionId2cMixIn(ProtoVersionIdMixInBase):
    apiAlphaProtoVersionId = rfc1905.Version().get()

# Stand-alone versions
class ProtoVersionIdBase:
    def __hash__(self): return hash(self.apiAlphaProtoVersionId)
    def __cmp__(self, other): return cmp(self.apiAlphaProtoVersionId, other)
    def __str__(self): return str(self.apiAlphaProtoVersionId+1)

class ProtoVersionId1(ProtoVersionIdBase, ProtoVersionId1MixIn): pass
class ProtoVersionId2c(ProtoVersionIdBase, ProtoVersionId2cMixIn): pass

mixInComps = [ (rfc1155, ProtoVersionId1MixIn),
               (rfc1157, ProtoVersionId1MixIn),
               (rfc1902, ProtoVersionId2cMixIn),
               (rfc1905, ProtoVersionId2cMixIn) ]

for (baseModule, mixIn) in mixInComps:
    for baseClass in map(lambda x, y=baseModule: getattr(y, x),
                         baseModule.__all__):
        if mixIn not in baseClass.__bases__:
            baseClass.__bases__ = (mixIn, ) + baseClass.__bases__
            
