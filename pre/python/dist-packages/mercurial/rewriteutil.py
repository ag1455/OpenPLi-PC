# rewriteutil.py - utility functions for rewriting changesets
#
# Copyright 2017 Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

from __future__ import absolute_import

from .i18n import _

from . import (
    error,
    node,
    obsolete,
    revset,
)


def precheck(repo, revs, action=b'rewrite'):
    """check if revs can be rewritten
    action is used to control the error message.

    Make sure this function is called after taking the lock.
    """
    if node.nullrev in revs:
        msg = _(b"cannot %s null changeset") % action
        hint = _(b"no changeset checked out")
        raise error.Abort(msg, hint=hint)

    if len(repo[None].parents()) > 1:
        raise error.Abort(_(b"cannot %s while merging") % action)

    publicrevs = repo.revs(b'%ld and public()', revs)
    if publicrevs:
        msg = _(b"cannot %s public changesets") % action
        hint = _(b"see 'hg help phases' for details")
        raise error.Abort(msg, hint=hint)

    newunstable = disallowednewunstable(repo, revs)
    if newunstable:
        raise error.Abort(_(b"cannot %s changeset with children") % action)


def disallowednewunstable(repo, revs):
    """Checks whether editing the revs will create new unstable changesets and
    are we allowed to create them.

    To allow new unstable changesets, set the config:
        `experimental.evolution.allowunstable=True`
    """
    allowunstable = obsolete.isenabled(repo, obsolete.allowunstableopt)
    if allowunstable:
        return revset.baseset()
    return repo.revs(b"(%ld::) - %ld", revs, revs)
