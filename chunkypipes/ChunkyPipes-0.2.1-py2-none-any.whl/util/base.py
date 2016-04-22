import os


class BaseCommand(object):
    argv = None
    options = {}
    chunky_home = (os.path.expanduser('~')
                   if 'CHUNKY_HOME' not in os.environ
                   else os.environ['CHUNKY_HOME'])
    home_pipelines = os.path.join(chunky_home, '.chunky', 'pipelines')
    home_configs = os.path.join(chunky_home, '.chunky', 'configs')

    def run(self):
        pass

    def usage(self):
        return 'default usage'

    def help_text(self):
        return 'default print help'

    def parse_options(self):
        pass

    def run_from_argv(self, argv=None):
        if argv:
            self.argv = argv
        self.run()
