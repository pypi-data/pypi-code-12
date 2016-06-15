# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
