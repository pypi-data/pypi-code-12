import os
import nose
import shutil
import yaml
from dryxDropboxCL import setup_selective_sync
from dryxDropboxCL.utKit import utKit

# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()
stream = file(pathToInputDir + "/general_settings.yaml", 'r')
settings = yaml.load(stream)

stream.close()

# xnose-class-to-test-main-command-line-function-of-module


class test_setup_selective_sync():

    def test_setup_selective_sync_function(self):
        kwargs = {}
        kwargs["log"] = log
        kwargs[
            "settings"] = settings
        # xt-kwarg_key_and_value

        setup_selective_sync(**kwargs)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
