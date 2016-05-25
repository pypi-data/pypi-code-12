import os
import imp


class BaseCommand(object):
    chunky_home = (os.path.expanduser('~')
                   if 'CHUNKY_HOME' not in os.environ
                   else os.environ['CHUNKY_HOME'])
    home_pipelines = os.path.join(chunky_home, '.chunky', 'pipelines')
    home_configs = os.path.join(chunky_home, '.chunky', 'configs')

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

    def help_text(self):
        return ''

    def run(self, command_args):
        return NotImplementedError

