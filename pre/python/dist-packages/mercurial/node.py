# node.py - basic nodeid manipulation for mercurial
#
# Copyright 2005, 2006 Matt Mackall <mpm@selenic.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

import binascii

# This ugly style has a noticeable effect in manifest parsing
hex = binascii.hexlify
# Adapt to Python 3 API changes. If this ends up showing up in
# profiles, we can use this version only on Python 3, and forward
# binascii.unhexlify like we used to on Python 2.
def bin(s):
    try:
        return binascii.unhexlify(s)
    except binascii.Error as e:
        raise TypeError(e)


nullrev = -1
# In hex, this is '0000000000000000000000000000000000000000'
nullid = b"\0" * 20
nullhex = hex(nullid)

# Phony node value to stand-in for new files in some uses of
# manifests.
# In hex, this is '2121212121212121212121212121212121212121'
newnodeid = b'!!!!!!!!!!!!!!!!!!!!'
# In hex, this is '3030303030303030303030303030306164646564'
addednodeid = b'000000000000000added'
# In hex, this is '3030303030303030303030306d6f646966696564'
modifiednodeid = b'000000000000modified'

wdirfilenodeids = {newnodeid, addednodeid, modifiednodeid}

# pseudo identifiers for working directory
# (they are experimental, so don't add too many dependencies on them)
wdirrev = 0x7FFFFFFF
# In hex, this is 'ffffffffffffffffffffffffffffffffffffffff'
wdirid = b"\xff" * 20
wdirhex = hex(wdirid)


def short(node):
    return hex(node[:6])
