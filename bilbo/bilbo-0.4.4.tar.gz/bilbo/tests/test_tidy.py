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


class test_tidy():

    def test_clean_filenames_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.clean_filenames(
            rootFolder=destinationWiki1
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
            wikiRoot=destinationWiki1,
            wikiName="testwiki1"
        )
        # x-print-testpage-for-pessto-marshall-web-object

    def test_except_marker_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.add_excerpt_marker(
            rootDirectory=destinationWiki1
        )

    def test_rename_scratch_files_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.rename_markdownfile_files_to_metadata_title(
            rootDirectory=destinationWiki1 + "/scratch"
        )

    def test_move_files_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.move_files_to_category_folders(
            wikiRoot=destinationWiki1
        )

    def test_transfer_files_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.transfer_pages_between_wikis(
            wikiRoot=destinationWiki1,
            wikiName="testwiki1"
        )

    def test_tidy_categories_function(self):

        from bilbo import tidy
        scrubber = tidy(
            log=log,
            settings=settings
        )
        scrubber.move_single_category_files_into_dedicated_folder(
            wikiRoot=destinationWiki1
        )

    # x-class-to-test-named-worker-function
