import os
import sys
import cli.configuration
from git import Repo


class Git():
    def __init__(self, property_data, user_data, directory):
        self.user_data = user_data
        self.property_data = property_data
        if directory is not None:
            self.repo_dest = os.path.join(os.getcwd() + '/%s' % directory)
        else:
            self.repo_dest = os.path.join(os.getcwd() + '/%s' % self.property_data['code'].lower())

    def init_repo(self):
        username = self.user_data['bitbucket_username']
        password = self.user_data['bitbucket_password']
        repository = self.property_data['bitbucket_repository']
        url = cli.configuration.BITBUCKET_URL % {
            'username': username,
            'password': password,
            'repository': repository
        }
        if self.property_data['bitbucket_repository']:
            try:
                Repo.clone_from(url, self.repo_dest, branch=cli.configuration.DEFAULT_GIT_BRANCH, progress=False)
                print 'Successfully initialized repo for %s in %s.' %(repository, self.repo_dest)
            except:
                print 'Failed to initialize Git repository. Exiting.'
                sys.exit()
        else:
            print "FATAL: Repository not found. Exiting."