#!/usr/bin/env python
from cleo import Command, InputArgument, InputOption
from cleo import Application
from probe.cloud import Cloud
import pkg_resources
import shutil
import os
import logging
import sys

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class CheckCommand(Command):
    name = 'cloud:check'

    description = 'returns all compures where is AD running right now'

    options = [
        {
            'name': 'config',
            'description': 'path to config file',
            'value_required': True,
            'default': 'cloud.cfg',
        }
    ]

    @staticmethod
    def execute(i, o):

        rdirwatcher_cfg = i.get_option('config')
        cloud = Cloud(rdirwatcher_cfg)
        cloud.check()

class RunSimulationCommand(Command):
    name = 'cloud:run_simulation'
    description = 'run simulation on cloud'

    options = [
        {
            'name': 'config',
            'description': 'path to config file',
            'value_required': True,
            'default': 'cloud.cfg',
        }
    ]

    @staticmethod
    def execute(i, o):
        rdirwatcher_cfg = i.get_option('config')
        cloud = Cloud(rdirwatcher_cfg)
        cloud.run_simulation()

class GetCfgCommand(Command):
    name = 'cloud:get_cfg'
    description = 'get cloud config file'

    arguments = [
        {
            'name': 'dest',
            'description': 'relative path where to put config file',
            'required': False,
            'default': '.',
        }
    ]

    @staticmethod
    def execute(i, o):
        dest = i.get_argument('dest')
        path_cfg = pkg_resources.resource_filename('probe.cloud', 'cfg/cloud.cfg')
        shutil.copyfile(path_cfg, os.path.join(dest, 'cloud.cfg'))

class GetFabfileCommand(Command):
    name = 'cloud:get_fabfile'
    description = 'get cloud fabfile'

    arguments = [
        {
            'name': 'dest',
            'description': 'relative path where to put fabfile',
            'required': False,
            'default': '.',
        }
    ]

    @staticmethod
    def execute(i, o):
        dest = i.get_argument('dest')
        path_cfg = pkg_resources.resource_filename('probe.cloud', 'fabfile.py')
        shutil.copyfile(path_cfg, os.path.join(dest, 'fabfile.py'))

if __name__ == '__main__':

    application = Application()
    application.add(CheckCommand())
    application.add(RunSimulationCommand())
    application.add(GetCfgCommand())
    application.add(GetFabfileCommand())
    application.run()
