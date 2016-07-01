import os
import nose
import shutil
import yaml
from bilbo import scaffold, cl_utils
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


class test_scaffold():

    def test_scaffold_function(self):

        from bilbo import scaffold
        this = scaffold(
            log=log,
            settings=settings
        )
        this.update_root_sidebar(
            rootDirectory=destinationWiki,
        )

    def test_get_function(self):

        from bilbo import scaffold
        this = scaffold(
            log=log,
            settings=settings
        )
        this.get()

    def test_root_home_page_function(self):

        from bilbo import scaffold
        this = scaffold(
            log=log,
            settings=settings
        )
        this.update_root_home_pages(
            rootDirectory=destinationWiki
        )

    def test_blogging_admin_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.clean_markdown_metadata(
            wikiRoot=destinationWiki,
            wikiName="testwiki1"
        )

        from bilbo import scaffold
        this = scaffold(
            log=log,
            settings=settings
        )
        (blogged, notblogged, unblogged, drafts) = this._get_blogging_workflow_pages(
            wikiRoot=destinationWiki
        )
        # print blogged, notblogged, unblogged
        this.create_blog_listings(
            wikiRoot=destinationWiki
        )

    def test_tag_admin_function(self):

        from bilbo import scaffold
        this = scaffold(
            log=log,
            settings=settings
        )
        (tags, untagged) = this._get_all_wiki_tags(
            wikiRoot=destinationWiki
        )
        print tags, untagged
        this.create_tag_listings(
            wikiRoot=destinationWiki
        )

    # x-class-to-test-named-worker-function
