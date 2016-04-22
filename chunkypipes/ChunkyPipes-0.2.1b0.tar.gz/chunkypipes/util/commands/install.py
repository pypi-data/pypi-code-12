import sys
import os
import shutil
from chunkypipes.util.base import BaseCommand

ARGV_PIPELINE_NAME = 0
EXIT = 0
EXIT_CMD_SYNTAX_ERROR = 2


class Command(BaseCommand):
    def usage(self):
        return 'Usage: chunky install <pipeline>.'

    def help_text(self):
        return 'Install a new pipeline\n ' \
               'Example: chunky install my_pipeline.py\n'

    def run(self):
        # Checks to see if they entered a pipeline name
        if not self.argv:
            #sys.stdout.write('No pipeline provided to install.\n')
            sys.stdout.write(self.usage() + '\n')
            sys.exit(EXIT_CMD_SYNTAX_ERROR)

        # Get pipeline name from argv
        pipeline_name = self.argv[ARGV_PIPELINE_NAME]

        if os.path.isfile('{}'.format(pipeline_name)) is False:
            sys.stdout.write('Pipeline not found\n')
            sys.exit(EXIT)

        # Helper to check if pipeline exists
        pipeline_filepath = os.path.join(self.home_pipelines,
                                         pipeline_name)

        # Check if pipeline already exists
        if os.path.isfile(pipeline_filepath):
            overwrite = raw_input('Pipeline {} is already installed, overwrite? [y/n] '.format(
                    pipeline_name
            ))
            no_set = {'no', 'n'}
            # Terminate if user says no
            if overwrite.lower() in no_set:
                sys.exit(EXIT)

        # Make sure they don't input the wrong name
        try:
            shutil.copy2(pipeline_name, self.home_pipelines)
            sys.stdout.write('Pipeline {} successfully installed\n'.format(pipeline_name))
        except (IOError, OSError, shutil.Error):
            sys.stdout.write('Pipeline {} not found\n'.format(pipeline_name))
            sys.exit(EXIT)
