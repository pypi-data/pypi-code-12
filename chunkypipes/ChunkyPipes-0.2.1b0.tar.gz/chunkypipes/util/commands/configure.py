import sys
import os
import imp
import argparse
import json
import readline
from chunkypipes.util.base import BaseCommand

ARGV_PIPELINE_NAME = 0
EXIT_CMD_SYNTAX_ERROR = 2

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind('tab: complete')


class Command(BaseCommand):
    def usage(self):
        return 'Usage: chunky configure <pipeline> [configure_options]'

    def help_text(self):
        help_msg = 'Create a configuration file for a pipeline.'
        return '\n'.join([self.usage(), help_msg])

    def get_pipeline_class(self, pipeline_name):
        pipeline_filepath = os.path.join(self.home_pipelines,
                                         '{}.py'.format(pipeline_name))

        # Look for pipeline in installed directory first
        if os.path.isfile(pipeline_filepath):
            return imp.load_source(pipeline_name,
                                   pipeline_filepath.format(pipeline_name)).Pipeline()
        # Check to see if pipeline name is a full path to pipeline
        elif os.path.isfile(pipeline_name):
            return imp.load_source('', pipeline_name).Pipeline()
        # If none of the above, return None
        return None

    def configure(self, config_dict):
        for key in config_dict:
            if type(config_dict[key]) == dict:
                self.configure(config_dict[key])
            else:
                prompt = config_dict[key].strip().strip(':')
                config_dict[key] = raw_input(prompt + ': ')

    def run(self):
        # Check to see a minimum number of arguments
        if not self.argv:
            sys.stdout.write('No pipeline provided to configure.\n')
            sys.stdout.write(self.usage() + '\n')
            sys.exit(EXIT_CMD_SYNTAX_ERROR)

        # Get pipeline name from argv and pipeline class from name
        pipeline_name = self.argv[ARGV_PIPELINE_NAME]
        pipeline_class = self.get_pipeline_class(pipeline_name)

        # Parse agruments from argv
        if pipeline_class:
            parser = argparse.ArgumentParser(prog='chunky configure {}'.format(pipeline_name))
            parser.add_argument('--location',
                                default=os.path.join(self.home_configs,
                                                     '{}.json'.format(pipeline_name)),
                                help='Path to which to save this config file. Defaults to install directory.')
            save_location = vars(parser.parse_args(self.argv[1:]))['location']

            # If this config already exists, prompt user before overwrite
            if os.path.isfile(save_location):
                overwrite = raw_input('Config for {} already exists at {}, overwrite? [y/n] '.format(
                    pipeline_name,
                    save_location
                ))
                no_set = {'no', 'n'}

                # If user responds no, exit immediately
                if overwrite.lower() in no_set:
                    sys.exit(0)

            # Get configuration from pipeline, recursively prompt user to fill in info
            config_dict = pipeline_class.configure()
            try:
                self.configure(config_dict)
            except (KeyboardInterrupt, EOFError):
                sys.stdout.write('\nUser aborted configuration.\n')
                sys.exit(0)

            # Write config out to file
            with open(save_location, 'w') as config_output:
                config_output.write(json.dumps(config_dict, indent=4) + '\n')
        # If pipeline doesn't exist, exit immediately
        else:
            sys.stdout.write('Pipeline {name} does not exist in {home}\n'.format(
                name=pipeline_name,
                home=self.home_pipelines + '/'
            ))
            sys.exit(EXIT_CMD_SYNTAX_ERROR)
