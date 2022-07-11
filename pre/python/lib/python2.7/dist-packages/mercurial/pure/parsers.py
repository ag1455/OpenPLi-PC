# parsers.py - Python implementation of parsers.c
#
# Copyright 2009 Matt Mackall <mpm@selenic.com> and others
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

import struct
import zlib

from ..node import nullid, nullrev
from .. import (
    pycompat,
    util,
)

from ..revlogutils import nodemap as nodemaputil

stringio = pycompat.bytesio


_pack = struct.pack
_unpack = struct.unpack
_compress = zlib.compress
_decompress = zlib.decompress

# Some code below makes tuples directly because it's more convenient. However,
# code outside this module should always use dirstatetuple.
def dirstatetuple(*x):
    # x is a tuple
    return x


indexformatng = b">Qiiiiii20s12x"
indexfirst = struct.calcsize(b'Q')
sizeint = struct.calcsize(b'i')
indexsize = struct.calcsize(indexformatng)


def gettype(q):
    return int(q & 0xFFFF)


def offset_type(offset, type):
    return int(int(offset) << 16 | type)


class BaseIndexObject(object):
    @property
    def nodemap(self):
        msg = b"index.nodemap is deprecated, use index.[has_node|rev|get_rev]"
        util.nouideprecwarn(msg, b'5.3', stacklevel=2)
        return self._nodemap

    @util.propertycache
    def _nodemap(self):
        nodemap = nodemaputil.NodeMap({nullid: nullrev})
        for r in range(0, len(self)):
            n = self[r][7]
            nodemap[n] = r
        return nodemap

    def has_node(self, node):
        """return True if the node exist in the index"""
        return node in self._nodemap

    def rev(self, node):
        """return a revision for a node

        If the node is unknown, raise a RevlogError"""
        return self._nodemap[node]

    def get_rev(self, node):
        """return a revision for a node

        If the node is unknown, return None"""
        return self._nodemap.get(node)

    def _stripnodes(self, start):
        if '_nodemap' in vars(self):
            for r in range(start, len(self)):
                n = self[r][7]
                del self._nodemap[n]

    def clearcaches(self):
        self.__dict__.pop('_nodemap', None)

    def __len__(self):
        return self._lgt + len(self._extra)

    def append(self, tup):
        if '_nodemap' in vars(self):
            self._nodemap[tup[7]] = len(self)
        self._extra.append(tup)

    def _check_index(self, i):
        if not isinstance(i, int):
            raise TypeError(b"expecting int indexes")
        if i < 0 or i >= len(self):
            raise IndexError

    def __getitem__(self, i):
        if i == -1:
            return (0, 0, 0, -1, -1, -1, -1, nullid)
        self._check_index(i)
        if i >= self._lgt:
            return self._extra[i - self._lgt]
        index = self._calculate_index(i)
        r = struct.unpack(indexformatng, self._data[index : index + indexsize])
        if i == 0:
            e = list(r)
            type = gettype(e[0])
            e[0] = offset_type(0, type)
            return tuple(e)
        return r


class IndexObject(BaseIndexObject):
    def __init__(self, data):
        assert len(data) % indexsize == 0
        self._data = data
        self._lgt = len(data) // indexsize
        self._extra = []

    def _calculate_index(self, i):
        return i * indexsize

    def __delitem__(self, i):
        if not isinstance(i, slice) or not i.stop == -1 or i.step is not None:
            raise ValueError(b"deleting slices only supports a:-1 with step 1")
        i = i.start
        self._check_index(i)
        self._stripnodes(i)
        if i < self._lgt:
            self._data = self._data[: i * indexsize]
            self._lgt = i
            self._extra = []
        else:
            self._extra = self._extra[: i - self._lgt]


class InlinedIndexObject(BaseIndexObject):
    def __init__(self, data, inline=0):
        self._data = data
        self._lgt = self._inline_scan(None)
        self._inline_scan(self._lgt)
        self._extra = []

    def _inline_scan(self, lgt):
        off = 0
        if lgt is not None:
            self._offsets = [0] * lgt
        count = 0
        while off <= len(self._data) - indexsize:
            (s,) = struct.unpack(
                b'>i', self._data[off + indexfirst : off + sizeint + indexfirst]
            )
            if lgt is not None:
                self._offsets[count] = off
            count += 1
            off += indexsize + s
        if off != len(self._data):
            raise ValueError(b"corrupted data")
        return count

    def __delitem__(self, i):
        if not isinstance(i, slice) or not i.stop == -1 or i.step is not None:
            raise ValueError(b"deleting slices only supports a:-1 with step 1")
        i = i.start
        self._check_index(i)
        self._stripnodes(i)
        if i < self._lgt:
            self._offsets = self._offsets[:i]
            self._lgt = i
            self._extra = []
        else:
            self._extra = self._extra[: i - self._lgt]

    def _calculate_index(self, i):
        return self._offsets[i]


def parse_index2(data, inline):
    if not inline:
        return IndexObject(data), None
    return InlinedIndexObject(data, inline), (0, data)


def parse_dirstate(dmap, copymap, st):
    parents = [st[:20], st[20:40]]
    # dereference fields so they will be local in loop
    format = b">cllll"
    e_size = struct.calcsize(format)
    pos1 = 40
    l = len(st)

    # the inner loop
    while pos1 < l:
        pos2 = pos1 + e_size
        e = _unpack(b">cllll", st[pos1:pos2])  # a literal here is faster
        pos1 = pos2 + e[4]
        f = st[pos2:pos1]
        if b'\0' in f:
            f, c = f.split(b'\0')
            copymap[f] = c
        dmap[f] = e[:4]
    return parents


def pack_dirstate(dmap, copymap, pl, now):
    now = int(now)
    cs = stringio()
    write = cs.write
    write(b"".join(pl))
    for f, e in pycompat.iteritems(dmap):
        if e[0] == b'n' and e[3] == now:
            # The file was last modified "simultaneously" with the current
            # write to dirstate (i.e. within the same second for file-
            # systems with a granularity of 1 sec). This commonly happens
            # for at least a couple of files on 'update'.
            # The user could change the file without changing its size
            # within the same second. Invalidate the file's mtime in
            # dirstate, forcing future 'status' calls to compare the
            # contents of the file if the size is the same. This prevents
            # mistakenly treating such files as clean.
            e = dirstatetuple(e[0], e[1], e[2], -1)
            dmap[f] = e

        if f in copymap:
            f = b"%s\0%s" % (f, copymap[f])
        e = _pack(b">cllll", e[0], e[1], e[2], e[3], len(f))
        write(e)
        write(f)
    return cs.getvalue()
