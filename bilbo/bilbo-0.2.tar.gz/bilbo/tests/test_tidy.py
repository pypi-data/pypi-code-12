import os
import nose
import shutil
import yaml
from bilbo import tidy, cl_utils
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


class test_tidy():

    def test_clean_filenames_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.clean_filenames(
            rootFolder=destinationWiki
        )

    def test_tidy_get_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.get()

    def test_clean_md_metadata_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.clean_markdown_metadata(
            wikiRoot=destinationWiki
        )
        # x-print-testpage-for-pessto-marshall-web-object

    def test_except_marker_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.add_excerpt_marker(
            rootDirectory=destinationWiki
        )

    def test_rename_scratch_files_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.rename_markdownfile_files_to_metadata_title(
            rootDirectory=destinationWiki + "/scratch"
        )

    def test_move_files_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.move_files_to_category_folders(
            wikiRoot=destinationWiki
        )

    # x-class-to-test-named-worker-function
