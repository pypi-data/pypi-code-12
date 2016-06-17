import os
import nose
import shutil
# from dryxDropboxCL import start_if_not_running
from dryxDropboxCL.utKit import utKit

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

# xnose-class-to-test-main-command-line-function-of-module


class test_start_if_not_running():

    def test_start_if_not_running_function(self):
        kwargs = {}
        kwargs["log"] = log
        # xt-kwarg_key_and_value

        start_if_not_running(**kwargs)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
