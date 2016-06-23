import os
import nose
import shutil
import yaml
from bilbo import templates, cl_utils
from bilbo.utKit import utKit

from fundamentals import tools

su = tools(
    arguments={"settingsFile": None},
    docString=__doc__,
    logLevel="DEBUG",
    options_first=False,
    projectName="bilbo",
    tunnel=False
)
arguments, settings, log, dbConn = su.setup()

# load settings
moduleDirectory = os.path.dirname(__file__)
stream = file(
    moduleDirectory + "/bilbo.yaml", 'r')
settings = yaml.load(stream)
stream.close()


# SETUP AND TEARDOWN FIXTURE FUNCTIONS FOR THE ENTIRE MODULE
moduleDirectory = os.path.dirname(__file__)
utKit = utKit(moduleDirectory)
log, dbConn, pathToInputDir, pathToOutputDir = utKit.setupModule()
utKit.tearDownModule()

sourceWiki = pathToInputDir + "/my-test-wiki"
destinationWiki = pathToOutputDir + "/my-test-wiki"
try:
    shutil.rmtree(destinationWiki)
except Exception, e:
    pass
shutil.copytree(sourceWiki, destinationWiki)

sourceWiki = pathToInputDir + "/my-test-wiki-2"
destinationWiki = pathToOutputDir + "/my-test-wiki-2"
try:
    shutil.rmtree(destinationWiki)
except Exception, e:
    pass

shutil.copytree(sourceWiki, destinationWiki)


class test_templates():

    def test_templates_function(self):
        from bilbo import templates
        templates(
            log=log,
            settings=settings
        ).get()

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
