# revlogdeltas.py - constant used for revlog logic
#
# Copyright 2005-2007 Matt Mackall <mpm@selenic.com>
# Copyright 2018 Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""Helper class to compute deltas stored inside revlogs"""

from __future__ import absolute_import

from ..interfaces import repository

# revlog header flags
REVLOGV0 = 0
REVLOGV1 = 1
# Dummy value until file format is finalized.
# Reminder: change the bounds check in revlog.__init__ when this is changed.
REVLOGV2 = 0xDEAD
# Shared across v1 and v2.
FLAG_INLINE_DATA = 1 << 16
# Only used by v1, implied by v2.
FLAG_GENERALDELTA = 1 << 17
REVLOG_DEFAULT_FLAGS = FLAG_INLINE_DATA
REVLOG_DEFAULT_FORMAT = REVLOGV1
REVLOG_DEFAULT_VERSION = REVLOG_DEFAULT_FORMAT | REVLOG_DEFAULT_FLAGS
REVLOGV1_FLAGS = FLAG_INLINE_DATA | FLAG_GENERALDELTA
REVLOGV2_FLAGS = FLAG_INLINE_DATA

# revlog index flags

# For historical reasons, revlog's internal flags were exposed via the
# wire protocol and are even exposed in parts of the storage APIs.

# revision has censor metadata, must be verified
REVIDX_ISCENSORED = repository.REVISION_FLAG_CENSORED
# revision hash does not match data (narrowhg)
REVIDX_ELLIPSIS = repository.REVISION_FLAG_ELLIPSIS
# revision data is stored externally
REVIDX_EXTSTORED = repository.REVISION_FLAG_EXTSTORED
# revision data contains extra metadata not part of the official digest
REVIDX_SIDEDATA = repository.REVISION_FLAG_SIDEDATA
REVIDX_DEFAULT_FLAGS = 0
# stable order in which flags need to be processed and their processors applied
REVIDX_FLAGS_ORDER = [
    REVIDX_ISCENSORED,
    REVIDX_ELLIPSIS,
    REVIDX_EXTSTORED,
    REVIDX_SIDEDATA,
]

# bitmark for flags that could cause rawdata content change
REVIDX_RAWTEXT_CHANGING_FLAGS = (
    REVIDX_ISCENSORED | REVIDX_EXTSTORED | REVIDX_SIDEDATA
)

SPARSE_REVLOG_MAX_CHAIN_LENGTH = 1000
