"""Run all the test-suites"""
import unittest, types

from twistedsnmp.test import test_get, test_set, test_storage, test_basic

def moduleSuite( module ):
	return unittest.TestLoader().loadTestsFromModule( module )

suite = unittest.TestSuite( [
	moduleSuite( module )
	for module in [
		test_basic,
		test_get,
		test_set,
		test_storage,
	]
])

if __name__ == "__main__":
	DO_HOTSHOT = 0
	DO_PROFILE = 0
	DO_MEMLEAK = 0
	DO_PSYCO = 0
	if DO_PSYCO:
		import psyco
		#from pysnmp.asn1 import base
		#psyco.bind(base.Asn1Object)
		psyco.full()
	if DO_PROFILE:
		command = """unittest.TextTestRunner(verbosity=2).run( suite )"""
		profileFile = 'last_run.profile'
		if DO_HOTSHOT:
			import hotshot
			profiler = hotshot.Profile( profileFile, lineevents=0 )
			profiler.runctx( command, globals(), locals())
			profiler.close()
		else:
			import profile
			p = profile.Profile()
			p.runctx( command, globals(), locals())
			p.print_stats()
			p.dump_stats(profileFile)
	else:
		if DO_MEMLEAK:
			import gc
			while 1:
				unittest.TextTestRunner(verbosity=2).run( suite )
				#print 'collection', gc.collect()
				
		else:
			unittest.TextTestRunner(verbosity=2).run( suite )
		
	