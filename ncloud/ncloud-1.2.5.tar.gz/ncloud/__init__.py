# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
command line interface for Nervana's deep learning cloud.
"""
import logging
import sys

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger()

try:
    from ncloud.version import VERSION as __version__  # noqa
except ImportError:
    logger.fatal("Version information not found.  Ensure you have built "
                 "the software.\n    From the top level dir issue: "
                 "'make install'")
    sys.exit(1)
