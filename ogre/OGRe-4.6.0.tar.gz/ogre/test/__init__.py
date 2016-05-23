"""
OpenFusion GeoJSON Retriever Tests

:mod:`test_api` -- query handling tests

:mod:`test_Twitter` -- Twitter interface tests

:mod:`test_validation` -- parameter validation and sanitation tests
"""

import logging

logging.basicConfig(
    filename="/var/tmp/ogre.test.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(name)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.getLogger(__name__).debug("Testing OGRe...")
