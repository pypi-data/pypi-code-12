import sys
import os
import argparse
import json
from chunkypipes.util.commands import BaseCommand

ARGV_PIPELINE_NAME = 0
EXIT_CMD_SUCCESS = 0
EXIT_CMD_SYNTAX_ERROR = 2


class Command(BaseCommand):
    @staticmethod
    def usage():
        return 'chunky show <pipeline-line> [-h]'

    def help_text(self):
        return ('Show information about a ChunkyPipes installed pipeline, including parameters, the ' +
                'configuration dictionary, and the current default configuration, if it exists.')

    def run(self, command_args):
        parser = argparse.ArgumentParser(prog='chunky show', usage=self.usage(), description=self.help_text())
        parser.add_argument('pipeline-name', help='ChunkyPipes pipeline to show.')
        pipeline_name = vars(parser.parse_args(command_args))['pipeline-name']
        if pipeline_name.lower() == 'help':
            parser.print_help()
            sys.exit(EXIT_CMD_SUCCESS)

        pipeline_class = self.get_pipeline_class(pipeline_name)
        config_dictionary = pipeline_class.configure()

        # Start show subcommand output
        sys.stdout.write('ChunkyPipes pipeline: {}\n\n'.format(pipeline_name))

        # Show pipeline arguments
        show_parser = argparse.ArgumentParser(prog='chunky run {}'.format(pipeline_name),
                                              description=pipeline_class.description())
        pipeline_class.add_pipeline_args(show_parser)
        show_parser.print_help()

        # Show pipeline dependencies
        sys.stdout.write('\nPipeline Dependencies:\n')
        if pipeline_class.dependencies():
            pipeline_class._print_dependencies()
        else:
            sys.stdout.write('None\n')

        # Show current platform configuration, if it exists
        config_json_filepath = os.path.join(self.home_configs, '{}.json'.format(pipeline_name))
        if os.path.isfile(config_json_filepath):
            sys.stdout.write('\nCurrent Configuration:\n')
            sys.stdout.write(open(config_json_filepath).read())

        # Show configuration dictionary, with prompts
        sys.stdout.write('\nConfiguration Dictionary:\n')
        sys.stdout.write(json.dumps(config_dictionary, indent=4) + '\n')
