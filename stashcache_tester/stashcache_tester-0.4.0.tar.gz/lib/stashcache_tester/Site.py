from jinja2 import Environment, FileSystemLoader

import logging
import os
from stashcache_tester.util import Configuration


class Site:
    """
    Class describing a site to be tested.
    
    This class creates the personalized tests for a single site.
    """
    def __init__(self, siteName):
        """
        :param str siteName: Site name to use in submit requirements.
        """
        self.siteName = siteName
        
        
    def createTest(self, testDir, jinjaEnvironment):
        """
        Create the test for a site.
        
        :param jinjaEnvironment: The Jinja2 environment from which to load templates.
        :param str testDir: Directory name to install tests
        :return: Filename of the site specific submit file
        """
        logging.debug("Creating personalized test for site %s in directory %s" % (self.siteName, testDir))
        
        site_testDir = os.path.join(testDir, self.siteName)
        
        # Create the site specific directory
        try:
            os.makedirs(site_testDir)
        except IOError as e:
            logging.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        
        # First, read in the submit template
        submit_template = jinjaEnvironment.get_template("site_submit.tmpl")
        with open(os.path.join(site_testDir, "submit.condor"), 'w') as f:
            f.write(submit_template.render({"numsubmit": int(self.get_option("numtests"))}))
        
        test_template = jinjaEnvironment.get_template("site_test.tmpl")
        with open(os.path.join(site_testDir, "site_test.sh"), 'w') as f:
            f.write(test_template.render())
        
            
        return os.path.join(site_testDir, "submit.condor")
        
        
    def get_option(self, option, default=None):
        
        return Configuration.get_option(option, default, self.siteName)
        
