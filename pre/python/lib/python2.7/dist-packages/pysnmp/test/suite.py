"""A test suite for PySNMP package"""
from  pysnmp.test import base, getset, trap, walk

suite = base.unittest.TestSuite( \
    map(lambda x: base.unittest.TestLoader().loadTestsFromModule(x), \
        [ getset, trap, walk ]))

def run():
    base.unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__': run()
