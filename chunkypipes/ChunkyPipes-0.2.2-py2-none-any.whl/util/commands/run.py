import argparse
import imp
import os
import sys
from chunkypipes.util.base import BaseCommand

ARGV_PIPELINE_NAME = 0
EXIT_CMD_SYNTAX_ERROR = 2


class Command(BaseCommand):
    pipeline_name = None
    pipeline_class = None
    options_parser = None
    options = None

    def usage(self):
        return 'Usage: chunky run <pipeline> [pipeline_options]'

    def help_text(self):
        help_msg = 'Run a pipeline with specified parameters.'
        return '\n'.join([self.usage(), help_msg])

    def get_pipeline_class(self):
        pipeline_filepath = os.path.join(self.home_pipelines,
                                         '{}.py'.format(self.pipeline_name))

        # Look for pipeline in installed directory first
        if os.path.isfile(pipeline_filepath):
            return imp.load_source(self.pipeline_name,
                                   pipeline_filepath.format(self.pipeline_name)).Pipeline()
        # Check to see if pipeline name is a full path to pipeline
        elif os.path.isfile(self.pipeline_name):
            return imp.load_source('',
                                   self.pipeline_name).Pipeline()
        # If none of the above, return None
        return None

    def parse_options(self):
        # Create argument parser
        self.options_parser = argparse.ArgumentParser(prog='chunky run {}'.format(self.pipeline_name),
                                                      description=self.pipeline_class.description())

        # Add a config argument to every pipeline so user isn't locked into the installation home
        self.options_parser.add_argument('-c', '--config',
                                         default=os.path.join(self.home_configs, '{}.json'.format(self.pipeline_name)),
                                         help='Path to a config file to use for this run.')

        # Add pipeline specific arguments, parse arguments, and inject into pipeline class as dict
        self.pipeline_class.add_pipeline_args(self.options_parser)
        self.pipeline_class.pipeline_args = vars(self.options_parser.parse_args(self.argv[1:]))

    def run(self):
        # Check to see a minimum number of arguments
        if not self.argv:
            sys.stdout.write('No pipeline provided to run.\n')
            sys.stdout.write(self.usage() + '\n')
            sys.exit(EXIT_CMD_SYNTAX_ERROR)

        # Get pipeline name from argv and pipeline class from name
        self.pipeline_name = self.argv[ARGV_PIPELINE_NAME]
        self.pipeline_class = self.get_pipeline_class()

        # Parse arguments from argv
        if self.pipeline_class:
            self.parse_options()
            self.pipeline_class._parse_config()
            self.pipeline_class.run_pipeline(
                pipeline_args=self.pipeline_class.pipeline_args,
                pipeline_config=self.pipeline_class.pipeline_config
            )
        # If pipeline doesn't exist, exit immediately
        else:
            sys.stdout.write('Pipeline {name} does not exist in {home}\n'.format(
                name=self.pipeline_name,
                home=self.home_pipelines + '/'
            ))
            sys.exit(EXIT_CMD_SYNTAX_ERROR)
