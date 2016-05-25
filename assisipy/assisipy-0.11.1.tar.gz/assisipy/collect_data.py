#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool for collecting data logged by CASUs after an experiment.
"""

import yaml
from fabric.api import get, run, settings

import argparse
import os, errno

def mkdir_p(path):
    '''
    recursively create paths, and do not raise error if already exists

    source: http://stackoverflow.com/a/600612
    '''
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class DataCollector:
    """
    Class for automatically retrieving CASU logs.
    """

    def __init__(self, project_file_name, clean=False, logpath=None):
        """
        Parses the configuration file and initializes internal data structures.
        """

        self.clean = clean

        self.arena = {}
        self.dep = {}

        self.project_root = os.path.dirname(os.path.abspath(project_file_name))
        self.proj_name = os.path.splitext(os.path.basename(project_file_name))[0]

        if logpath is None or logpath == 'None':
            self.custom_logpath = False
            self.data_dir = 'data_' + self.proj_name
        else:
            self.custom_logpath = True
            self.data_dir = os.path.join(
                os.path.abspath(logpath),
                'data_' + self.proj_name)


        self.collected = False

        with open(project_file_name) as project_file:
            project = yaml.safe_load(project_file)

        # Read the .arena file
        with open(os.path.join(self.project_root, project['arena'])) as arena_file:
            self.arena = yaml.safe_load(arena_file)

        # Read the deployment file
        with open(os.path.join(self.project_root, project['dep'])) as dep_file:
            self.dep = yaml.safe_load(dep_file)

    def collect(self):
        """
        Collect the data to the local machine.
        """

        # Create data folder on local machine
        cwd = os.getcwd()
        if cwd != self.project_root and not self.custom_logpath:
        ##if cwd != self.project_root :
            print('Changing directory to {0}'.format(self.project_root))
            os.chdir(self.project_root)


        try:
            # attempt to create data directory (func is recursive if necessary)
            mkdir_p(self.data_dir)
            #os.mkdir(self.data_dir)
            print('Created folder {0}.'.format(self.data_dir))
        except OSError:
            # The data directory already exists
            # that's ok
            pass

        os.chdir(self.data_dir)

        # Download the data from deployment targets
        for layer in self.dep:
            try:
                os.mkdir(layer)
                print('Created folder {0}.'.format(layer))
            except OSError:
                # The directory already exists
                pass
            os.chdir(layer)
            for casu in self.dep[layer]:
                with settings(host_string = self.dep[layer][casu]['hostname'],
                              user = self.dep[layer][casu]['user'],
                              warn_only = True):
                    patterns = (['*.csv',] +
                            self.dep[layer][casu].get('results', []) )

                    for pattern in patterns:
                        targetfiles = os.path.join(self.dep[layer][casu]['prefix'],
                                layer, casu, pattern)
                        get(targetfiles,'.')
                        if self.clean:
                            run('rm ' + targetfiles)

            os.chdir('..')

        # Return to the original directory
        os.chdir(cwd)


def main():
    parser = argparse.ArgumentParser(description='Collect CASU logs. Currently assumes that the logs are located in the same folder as the controller.')
    parser.add_argument('project', help='Project file name (.assisi).')
    parser.add_argument('--logpath', default=None, help="override for path where logs will be written to")
    parser.add_argument('--clean', action='store_true', default=False,
                        help='Remove original log files after copying.')
    args = parser.parse_args()
    dc = DataCollector(args.project, args.clean, args.logpath)
    dc.collect()

if __name__ == '__main__':
    main()
