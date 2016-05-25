
import logging
import logging.handlers
import os, sys
import re
import subprocess
# TODO: possibly use PackageLoader
from jinja2 import Environment, FileSystemLoader
import shutil
import glob
import json
import hashlib

import humanfriendly
from stashcache_tester.Site import Site
from stashcache_tester.util.ExternalCommands import RunExternal
from stashcache_tester.util.Configuration import get_option, set_config_file, set_option

from stashcache_tester.util.StreamToLogger import StreamToLogger


class StashCacheTester(object):
    """Main class for the stash cache tester"""
    def __init__(self, configFiles):
        
        # First, read in the configuration
        set_config_file(configFiles)
        self.config_location = os.path.abspath(configFiles)
        
        loglevel = get_option("loglevel", default="warning", section="logging")
        logdirectory = get_option("logdirectory", default="log", section="logging")
        self._setLogging(loglevel, logdirectory)
        
        raw_testsize = humanfriendly.parse_size(get_option("testsize"))
        set_option("raw_testsize", raw_testsize)
            

        
    def _setLogging(self, loglevel, logdirectory):
        logging_levels = {'debug': logging.DEBUG,
                          'info': logging.INFO,
                          'warning': logging.WARNING,
                          'error': logging.ERROR,
                          'critical': logging.CRITICAL}

        level = logging_levels.get(loglevel)
        
        # Create the log directory, if it doesn't already exist
        if not os.path.isdir(logdirectory):
            os.makedirs(logdirectory)
        
        handler = logging.handlers.RotatingFileHandler(os.path.join(logdirectory, "stashcachetester.log"),
                        maxBytes=10000000, backupCount=5)
        root_logger = logging.getLogger()
        # Clear out the logger
        root_logger.handlers = []
        
        root_logger.setLevel(level)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        
        # Send stdout to the log
        stdout_logger = logging.getLogger()
        sl = StreamToLogger(stdout_logger, logging.INFO)
        sys.stdout = sl
 
        stderr_logger = logging.getLogger()
        sl = StreamToLogger(stderr_logger, logging.ERROR)
        sys.stderr = sl
        
    
    def get_sites(self):
        # First, get the sites from the configuration
        sites = get_option("sites")
        logging.debug("Got sites:\"%s\" from config file" % sites)
        if sites is None or sites is "":
            logging.error("No sites defined, therefore no tests created.")
            return None
        
        split_sites = re.split("[,\s]+", sites)
        return split_sites
    
    def runTests(self):
        """
        Run the tests prescribed in the configuration
        """
        sites = self.get_sites()
        templates_dir = os.path.join(sys.prefix, "etc/stashcache-tester/templates")
        
        # Parse the size of the test in bytes
        raw_testsize = humanfriendly.parse_size(get_option("testsize"))
        
        md5sum = self.createTestFile(raw_testsize, get_option("stashdir"))
        
        
        # Create the site specific tests
        env = Environment(loader=FileSystemLoader(templates_dir))
        
        
        
        env.globals = {
            "config_location": self.config_location,
            "stash_test_location": os.path.abspath(sys.argv[0]),
            "pythonpath": ":".join(sys.path),
            "testurl": get_option("testurl"),
            "localpath": get_option("stashdir"),
            "testsize": raw_testsize,
            "humantestsize": humanfriendly.format_size(raw_testsize)
        }
        
        test_dirs = []
        testingdir = get_option("testingdir")
        for site in sites:
            tmp_site = Site(site)
            test_dir = tmp_site.createTest(testingdir, env)
            test_dirs.append(test_dir)
        
        
        # Create the DAG from the template
        
        dag_template = env.get_template("dag.tmpl")
        test_dag = os.path.join(testingdir, "submit.dag")
        with open(test_dag, 'w') as f:
            f.write(dag_template.render(sites=sites, md5sum=md5sum))
            
        
        reduce_template = env.get_template("test_reduce.tmpl")
        reduce_submit = os.path.join(testingdir, "reduce.submit")
        with open(reduce_submit, 'w') as f:
            f.write(reduce_template.render())
            
        shutil.copyfile(os.path.join(templates_dir, "site_post.py"), os.path.join(get_option("testingdir"), "site_post.py"))
        os.chmod(os.path.join(get_option("testingdir"), "site_post.py"), 0755)
        
        # Start the DAG
        (stdout, stderr) = RunExternal("cd %s; condor_submit_dag submit.dag" % testingdir)
        logging.debug("output from condor_submit_dag: %s" % stdout)
        if stderr is not None or stderr is not "":
            logging.error("Error from condor_submit_dag: %s" % stderr)
        
    
    def createTestFile(self, size, location):
        """
        Create a file of size at location
        
        :param int size: size of the requested file
        :param str location: location to store test file
        :return: String md5sum
        :rtype: string
        """
        
        
        def md5(fname):
            hash_md5 = hashlib.md5()
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        
        if os.path.isfile(location):
            logging.warning("File %s already exists." % location)
            if size == os.path.getsize(location):
                logging.warning("File %s is the correct size, not modifying" % location)
                return md5(location)
            else:
                logging.warning("File %s is incorrect size.  Should be %i, was %i" % (location, size, os.path.getsize(location)))
                logging.warning("Removing %s in order to create correctly sized test file" % location)
                os.remove(location)
        
        # Now, create the file of the correct size
        with open(location, 'wb') as f:
            # block size of 10 MB
            blocksize = 10 * (1024*1024)
            while (size > 0):
                f.write(os.urandom(blocksize))
                size -= blocksize
            
        return md5(location)
    
        
    def reduceResults(self):
        """
        Reduce the results from the DAG to something useful
        """
        
        siteData = {}
        
        # Read in the results
        for site in self.get_sites():
            logging.info("Processing site %s" % site)
            inputdata = {}
            with open("postprocess.%s.json" % site) as f:
                inputdata = json.load(f)
            
            siteData[site] = inputdata
        
        outputmodule = ".".join(get_option("outputtype").split(".")[:-1])
        outputclass = get_option("outputtype").split(".")[-1]
        
        try:
            logging.debug("Trying to import module %s and class %s" % (outputmodule, outputclass))
            mod = __import__(outputmodule, fromlist=[outputclass])
            outputProcessor = getattr(mod, outputclass)
            outputProcessor = outputProcessor(siteData)
        
        except ImportError as e:
            logging.error("Failed to load module %s and class %s" % (outputmodule, outputclass))
            raise e
        
        outputProcessor.startProcessing()

            
        
