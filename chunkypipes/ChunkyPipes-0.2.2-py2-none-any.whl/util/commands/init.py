import os
import sys
from chunkypipes.util.base import BaseCommand

ARGV_CHUNKY_HOME_ROOT = 0


class Command(BaseCommand):
    @staticmethod
    def make_chunky_home(chunky_home_root):
        try:
            if not os.path.exists(os.path.join(chunky_home_root, '.chunky')):
                os.mkdir(os.path.join(chunky_home_root, '.chunky'))
            if not os.path.exists(os.path.join(chunky_home_root, '.chunky', 'pipelines')):
                os.mkdir(os.path.join(chunky_home_root, '.chunky', 'pipelines'))
            if not os.path.isfile(os.path.join(chunky_home_root, '.chunky', 'pipelines', '__init__.py')):
                os.mknod(os.path.join(chunky_home_root, '.chunky', 'pipelines', '__init__.py'), 0o644)
            if not os.path.exists(os.path.join(chunky_home_root, '.chunky', 'configs')):
                os.mkdir(os.path.join(chunky_home_root, '.chunky', 'configs'))

            sys.stdout.write('ChunkyPipes successfully initialized at {}\n'.format(chunky_home_root))

            if chunky_home_root != os.path.expanduser('~'):
                sys.stdout.write('Please set a CHUNKY_HOME environment variable to {}\n'.format(chunky_home_root))
        except OSError as e:
            sys.stderr.write('An error occurred initializing ChunkyPipes at {}.\n{}\n'.format(
                chunky_home_root,
                e.message
            ))

    def usage(self):
        return 'Usage: chunky init [chunky_home_root]'

    def help_text(self):
        help_msg = ('Initializes ChunkyPipes at the given location.\n\n' +
                    'If no path is given, the current working directory is used.\nThe user ' +
                    'needs to set the CHUNKY_HOME environment variable manually for\nChunkyPipes ' +
                    'to use the newly created directory.')
        return '\n'.join([self.usage(), help_msg])

    def run(self):
        if not self.argv:
            chunky_home_root = os.path.expanduser('~')
        else:
            chunky_home_root = os.path.abspath(self.argv[ARGV_CHUNKY_HOME_ROOT])
        self.make_chunky_home(chunky_home_root)
