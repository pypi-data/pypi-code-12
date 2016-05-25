import os
import sys
import argparse
from chunkypipes.util.commands import BaseCommand

BASENAME = 0
EXTENTION = 1


class Command(BaseCommand):
    def help_text(self):
        return 'Lists installed pipelines in the default ChunkyPipes home directory.'

    def run(self, command_args):
        # Get argparse help funtionality
        argparse.ArgumentParser(prog='chunky list', description=self.help_text()).parse_args(command_args)

        sys.stdout.write('Installed pipelines (in {}):\n\n'.format(self.home_pipelines))

        # Grab the installed files from both directories
        installed_pipelines = {os.path.splitext(pipeline)[BASENAME] for pipeline
                               in os.listdir(self.home_pipelines)
                               if pipeline != '__init__.py'}

        installed_configs = [config for config in os.listdir(self.home_configs)]

        for pipeline_name in installed_pipelines:
            if '{}.json'.format(pipeline_name) in installed_configs:
                print '{} is configured'.format(pipeline_name)
            else:
                print '{} is NOT configured'.format(pipeline_name)
