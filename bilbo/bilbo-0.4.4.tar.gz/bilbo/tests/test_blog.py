import os
import nose
import shutil
import yaml
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

sourceWiki1 = pathToInputDir + "/my-test-wiki"
destinationWiki1 = pathToOutputDir + "/my-test-wiki"
try:
    shutil.rmtree(destinationWiki1)
except Exception, e:
    pass
shutil.copytree(sourceWiki1, destinationWiki1)

sourceWiki2 = pathToInputDir + "/my-test-wiki-2"
destinationWiki2 = pathToOutputDir + "/my-test-wiki-2"
try:
    shutil.rmtree(destinationWiki2)
except Exception, e:
    pass

shutil.copytree(sourceWiki2, destinationWiki2)

postDir = pathToOutputDir + "/blog/_posts"
try:
    shutil.rmtree(postDir)
except:
    pass
# Recursively create missing directories
if not os.path.exists(postDir):
    os.makedirs(postDir)
privateDir = pathToOutputDir + "/blog/protected"
try:
    shutil.rmtree(privateDir)
except:
    pass
# Recursively create missing directories
if not os.path.exists(privateDir):
    os.makedirs(privateDir)


class test_blog():

    def test_blog_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.get()

        from bilbo import blog
        poster = blog(
            log=log,
            settings=settings
        )
        poster._send_flagged_pages_to_jekyll_posts(
            wikiRoot=destinationWiki1
        )

    def test_blog_function_exception(self):

        from bilbo import blog
        try:
            this = blog(
                log=log,
                settings=settings,
                fakeKey="break the code"
            )
            this.get()
            assert False
        except Exception, e:
            assert True
            print str(e)

        # x-print-testpage-for-pessto-marshall-web-object

    # x-class-to-test-named-worker-function
