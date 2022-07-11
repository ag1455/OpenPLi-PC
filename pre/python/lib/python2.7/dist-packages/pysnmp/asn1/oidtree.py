"""
   The assignments of the "top of the OID tree", according to
   X.208 (ASN.1) ITU-T recommendation.

   Written by Ilya Etingof <ilya@glas.net>, 2002.
"""
from pysnmp.asn1 import univ
    
class Internet(univ.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6).internet(1)'
    
class Dod(univ.ObjectIdentifier):
    initialValue = 'iso(1).org(3).dod(6)'
    initialChildren = [ Internet ]

class Org(univ.ObjectIdentifier):
    initialValue = 'iso(1).org(3)'
    initialChildren = [ Dod ]

class Iso(univ.ObjectIdentifier):
    initialValue = 'iso(1)'
    initialChildren = [ Org ]

class Root(univ.ObjectIdentifier):
    initialChildren = [ Iso ]
