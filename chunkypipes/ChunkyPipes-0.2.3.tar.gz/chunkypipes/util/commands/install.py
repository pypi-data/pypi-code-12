import sys
import os
import shutil
import argparse
from chunkypipes.util.commands import BaseCommand

ARGV_PIPELINE_NAME = 0
EXIT_CMD_SUCCESS = 0
EXIT_CMD_ERROR = 1
EXIT_CMD_SYNTAX_ERROR = 2


class Command(BaseCommand):
    @staticmethod
    def usage():
        return 'chunky install <pipeline-path> [-h]'

    def help_text(self):
        return 'Install a ChunkyPipes formatted pipeline.'

    def run(self, command_args):
        parser = argparse.ArgumentParser(prog='chunky install', usage=self.usage(), description=self.help_text())
        parser.add_argument('pipeline-path', help='Full path to a ChunkyPipes formatted pipeline to install.')
        pipeline_path = vars(parser.parse_args(command_args))['pipeline-path']
        if pipeline_path.lower() == 'help':
            parser.print_help()
            sys.exit(EXIT_CMD_SUCCESS)

        # Check if provided filepath actually exists
        if not os.path.isfile(pipeline_path):
            sys.stderr.write('Pipeline not {} found.\n'.format(pipeline_path))
            sys.exit(EXIT_CMD_SYNTAX_ERROR)

        # Check if pipeline already exists
        if os.path.isfile(os.path.join(self.home_pipelines, os.path.basename(pipeline_path))):
            overwrite = raw_input('Pipeline {} is already installed, overwrite? [y/n] '.format(
                    os.path.basename(pipeline_path)
            ))
            if overwrite.lower() in {'no', 'n'}:
                sys.exit(EXIT_CMD_SUCCESS)

        # Copy pipeline file
        try:
            shutil.copy2(pipeline_path, self.home_pipelines)
            sys.stdout.write('Pipeline {} successfully installed.\n'.format(os.path.basename(pipeline_path)))
        except (IOError, OSError, shutil.Error):
            sys.stdout.write('Pipeline at {} could not be installed into {}.\n'.format(pipeline_path,
                                                                                       self.home_pipelines))
            sys.exit(EXIT_CMD_SYNTAX_ERROR)

        # Attempt to install dependencies through pip
        try:
            from pip import main as pip
        except ImportError:
            sys.stderr.write('Your platform or virtual environment does not appear to have pip installed.\n')
            sys.stderr.write('Dependencies cannot be installed, skipping this step.\n')
            sys.exit(EXIT_CMD_ERROR)

        pipeline_class = self.get_pipeline_class(pipeline_path)
        pipeline_dependencies = pipeline_class.dependencies()
        if pipeline_dependencies:
            sys.stdout.write('\nAttempting to install the following dependencies:\n')
            pipeline_class._print_dependencies()
            install_depencencies = raw_input('\nProceed with dependency installation? [y/n] ')
            if install_depencencies.lower() in {'no', 'n'}:
                sys.exit(EXIT_CMD_SUCCESS)
            for package in pipeline_dependencies:
                pip(['install', '--upgrade', package])
