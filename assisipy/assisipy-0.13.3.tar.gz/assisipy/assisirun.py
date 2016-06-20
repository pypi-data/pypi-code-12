#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool for remotely running CASU controllers.
"""

# none of the fabric tools are used [directly], import removed
#from fabric.api import settings, cd, run, env

import yaml

#import os.path
import os
import argparse
import subprocess

class AssisiRun:
    """
    Remote execution tool.
    """
    def __init__(self, project_name):
        """
        Constructor.
        """

        self.proj_name = os.path.splitext(os.path.basename(project_name))[0]
        self.project_root = os.path.dirname(os.path.abspath(project_name))
        self.fabfile_name = self.proj_name + '.py'
        self.depspec = {}
        with open(project_name) as project:
            project_spec = yaml.safe_load(project)
            with open(os.path.join(self.project_root, project_spec['dep'])) as depfile:
                self.depspec = yaml.safe_load(depfile)

        # Running controllers
        self.running = {}

    def run(self):
        """
        Execute the controllers.
        """
        #env.parallel = True
        cwd = os.getcwd()
        print('Changing directory to {0}'.format(self.project_root))
        os.chdir(self.project_root)
        print('Preparing files for deployment!')
        counter = 0
        for layer in self.depspec:
            for casu in self.depspec[layer]:
                taskname = layer.replace('-','_') + '_' + casu.replace('-','_')
                cmd = 'fab -f {0} {1}'.format(self.fabfile_name, taskname)
                print(cmd)
                self.running[taskname] = subprocess.Popen(cmd,shell='True')

        for taskname in self.running:
            self.running[taskname].wait()

        # back to original directory.
        os.chdir(cwd)

def main():
    parser = argparse.ArgumentParser(description='Run a set of CASU controllers.')
    parser.add_argument('project', help='name of .assisi file specifying the project details.')
    args = parser.parse_args()

    project = AssisiRun(args.project)
    project.run()

if __name__ == '__main__':
    main()
