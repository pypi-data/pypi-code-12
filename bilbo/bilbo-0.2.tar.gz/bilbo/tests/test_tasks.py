import os
import nose
import shutil
import yaml
from bilbo import tasks, cl_utils
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


sourceTasks = pathToInputDir + "/my-projects.taskpaper"
destinationTasks = pathToOutputDir + "/my-projects.taskpaper"
try:
    os.remove(destinationTasks)
except Exception, e:
    pass

shutil.copyfile(sourceTasks, destinationTasks)


class test_tasks():

    def test_tasks_function(self):

        from bilbo import tasks
        this = tasks(
            log=log,
            settings=settings
        )
        this.get()

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
