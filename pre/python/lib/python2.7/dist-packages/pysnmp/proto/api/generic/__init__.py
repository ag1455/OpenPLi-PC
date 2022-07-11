"""
   SNMP framework for Python.

   The pysnmp.proto.api.generic sub-package implements a high-level
   API to various SNMP messages.

   NOTICE: this API has been considered obsolete in favor of a more
   accurate pysnmp.proto.api.alpha implementation.

   Copyright 1999-2004 by Ilya Etingof <ilya@glas.net>. See LICENSE for
   details.
"""
from pysnmp.proto.api.generic import rfc1157, rfc1905
map(lambda x: x.mixIn(), [ rfc1157, rfc1905 ])
