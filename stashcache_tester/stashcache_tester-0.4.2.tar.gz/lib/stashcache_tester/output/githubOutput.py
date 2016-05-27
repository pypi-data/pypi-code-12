
import logging
import json
import time
import shutil
import os
import sys
from tempfile import NamedTemporaryFile

from stashcache_tester.output.generalOutput import GeneralOutput
from stashcache_tester.util.Configuration import get_option
from stashcache_tester.util.ExternalCommands import RunExternal


class GithubOutput(GeneralOutput):
    """
    
    :param dict sitesData: Dictionary described in :ref:`sitesData <sitesData-label>`.
    
    This class summarizes and uploads the download data to a github account.  The data will be stored in a file named ``data.json`` in the git repo under the directory in the configuration.  The format of ``data.json`` is::
    
        {
            "20150911": [
                {
                    "average": 364.76526180827,
                    "name": "Tusker"
                },
                {
                    "average": 75.99734924610296,
                    "name": "UCSDT2"
                },
                ...
            ], 
            "20150913": [
                {
                    "average": 239.02169168535966,
                    "name": "Tusker"
                },
                ...
            ],
            ...
        }
    
    Github output requires an SSH key to be added to the github repository which is pointed to by the `repo` configuration option.
    
    Github output requires additional configuration options in the main configuration in the section `[github]`.  An example configuration could be::
    
        [github]
        repo = StashCache/stashcache.github.io.git
        branch = master
        directory = data
        ssh_key = /home/user/.ssh/id_rsa
        
        
    The configuration is:
    
    repo
        The git repo to commit the data to.
        
    branch
        The branch to install repo.
        
    directory
        The directory to put the data summarized files into.
        
    maxdays
        The maximum number of days to keep data.  Default=30
        
    ssh_key
        Path to SSH key to use when checking out and pushing to the repository.
        
    
    """
    
    git_ssh_contents = """#!/bin/sh
    
    exec ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i $SSH_KEY_FILE "$@"
    
    """
    
    def __init__(self, sitesData):
        GeneralOutput.__init__(self, sitesData)
        
        
    def _get_option(self, option, default = None):
        return get_option(option, section="github", default=default)
        
    
    def _summarize_data(self, sitesData):
        summarized = []
        
        # Average download time per site.
        for site in sitesData:
            cur = {}
            cur['name'] = site
            siteTimes = sitesData[site]
            total_runtime = 0
            failures = 0
            caches = {}
            for run in siteTimes:
                # Initialize the cache structure
                cache = run['cache']
                if cache not in caches:
                    caches[cache] = {}
                    caches[cache]['runs'] = 0
                    caches[cache]['totalRuntime'] = 0
                    caches[cache]['failures'] = 0
                    
                if run['success'] is True:
                    total_runtime += float(run['duration'])
                    caches[cache]['totalRuntime'] += float(run['duration'])
                    caches[cache]['runs'] += 1
                else:
                    caches[cache]['failures'] += 1
                    failures += 1
            
            
            
            testsize = get_option("raw_testsize")
            if total_runtime == 0:
                cur['average'] = 0
                for cache in caches.keys():
                    caches[cache]['average'] = 0
            else:
                cur['average'] = (float(testsize*8) / (1024*1024)) / (total_runtime / len(siteTimes))
                
                for cache in caches.keys():
                    caches[cache]['average'] = (float(testsize*8) / (1024*1024)) / (caches[cache]['totalRuntime'] / caches[cache]['runs'])
            
            cur['caches'] = caches
            cur['failures'] = failures
            
            summarized.append(cur)
            
        
        # Should we do violin plot?
        
        #summarized = sitesData 
        return summarized
        
    
    def startProcessing(self):
        """
        Begin summarizing the data.
        """
        
        summarized_data = self._summarize_data(self.sitesData)
        
        logging.debug("Creating temporary file for GIT_SSH")
        tmpfile = NamedTemporaryFile(delete=False)
        tmpfile.write(self.git_ssh_contents)
        git_sh_loc = tmpfile.name
        logging.debug("Wrote contents of git_ssh_contents to %s" % git_sh_loc)
        tmpfile.close()
        import stat
        os.chmod(git_sh_loc, stat.S_IXUSR | stat.S_IRUSR)
        os.environ["GIT_SSH"] = git_sh_loc
        
        # Download the git repo
        git_repo = self._get_option("repo")
        git_branch = self._get_option("branch")
        key_file = self._get_option("ssh_key")
        output_dir = self._get_option("directory")
        os.environ["SSH_KEY_FILE"] = key_file
        RunExternal("git clone --quiet --branch %s  git@github.com:%s output_git" % (git_branch, git_repo))
        
        # Write summarized data to the data file
        data_filename = os.path.join("output_git", output_dir, "data.json")
        if not os.path.exists(data_filename):
            logging.error("Data file does not exist, bailing")
            sys.exit(1)
        with open(data_filename) as data_file:
            data = json.load(data_file)
        
        # Truncate the data to the latest `maxdays` days.
        maxdays = self._get_option("maxdays", 30)
        # Get and sort the keys
        sorted_list = data.keys()
        sorted_list.sort()
        # Discard the last `maxdays` days (looking for what we need to delete)
        to_delete = sorted_list[:-int(maxdays)]
        for key in to_delete:
            logging.debug("Removing data from %s" % key)
            data.pop(key, None)
        
        # Write today's summarized data
        todays_key = time.strftime("%Y%m%d")
        data[todays_key] = summarized_data
        with open(data_filename, 'w') as data_file:
            json.dump(data, data_file)
        
        # Commit to git repo
        RunExternal("cd output_git; git add -f .")
        RunExternal("cd output_git; git commit -m \"Adding data for %s\"" % todays_key)
        RunExternal("cd output_git; git push -fq origin %s" % git_branch)
        
        shutil.rmtree("output_git")
        
