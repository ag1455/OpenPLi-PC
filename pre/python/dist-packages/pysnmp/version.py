"""Package version information
"""
import error

__versionMajor = 3
__versionMinor = 4
__patchLevel = 3

def getVersion(): return (__versionMajor, __versionMinor, __patchLevel)
def verifyVersionRequirement(versionMajor, versionMinor, patchLevel=0):
    if __versionMajor < versionMajor or \
       __versionMajor == versionMajor and __versionMinor < versionMinor:
        raise error.PySnmpVersionError(
            'PySNMP version %s.%s or higher required' %
            (versionMajor, versionMinor)
        )
    if __versionMajor == versionMajor and __versionMinor == versionMinor and \
           patchLevel > 0 and __patchLevel < patchLevel:
        raise error.PySnmpVersionError(
            'PySNMP version %s.%s (patch level %s) or higher required' %
            (versionMajor, versionMinor, patchLevel)
        )
