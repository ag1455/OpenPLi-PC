# nodemap.py - nodemap related code and utilities
#
# Copyright 2019 Pierre-Yves David <pierre-yves.david@octobus.net>
# Copyright 2019 George Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import
from .. import error


class NodeMap(dict):
    def __missing__(self, x):
        raise error.RevlogError(b'unknown node: %s' % x)
