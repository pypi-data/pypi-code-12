import os
import sys
from chunkypipes.util.base import BaseCommand


class Command(BaseCommand):

    def usage(self):
        return 'Usage: chunky list'

    def help_text(self):
        help_msg = 'Lists installed pipelines'
        return '\n'.join([self.usage(), help_msg])

    def run(self):
        sys.stdout.write('Installed pipelines (in {}):\n\n'.format(self.home_pipelines))

        # Grab the pipelines from both directories
        configured_pipelines = os.listdir(self.home_configs)
        all_pipelines = os.listdir(self.home_pipelines)
        pipeline_configuration = {}  # Dictionary for the pipelines
        j = ''  # variable to keep out duplicates

        # sort to avoid putting duplicates into dictionary
        all_pipelines.sort()

        # Put all pipelines in the library
        for i in all_pipelines:
            if j.split('.')[0] != i.split('.')[0]:  # if the previous pipeline has the same name, do not add
                pipeline_configuration[i.split('.')[0]] = 'NOT configured'
            j = i

        # Set the pipelines in the configured folder to configured
        for pipeline in configured_pipelines:
            pipeline_configuration[pipeline.split('.')[0]] = 'configured'
        # print the pipelines
        for pipeline, configuration in pipeline_configuration.iteritems():
            sys.stdout.write('{} is {}\n'.format(pipeline, configuration))