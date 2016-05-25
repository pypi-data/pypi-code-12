import os
import sys
import argparse
from chunkypipes.util.commands import BaseCommand

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

    @staticmethod
    def usage():
        return 'chunky init [chunky_home_root]'

    def help_text(self):
        return ('Initializes ChunkyPipes at the given location.\n\n' +
                'If no path is given, the user home directory is used.\n For any location other than ' +
                'the user home directory, the user ' +
                'needs to set a CHUNKY_HOME environment variable manually for\nChunkyPipes ' +
                'to use the newly created directory.')

    def run(self, command_args):
        parser = argparse.ArgumentParser(prog='chunky init', usage=self.usage(), description=self.help_text())
        parser.add_argument('chunky-home-root', default=os.path.expanduser('~'), nargs='?',
                            help=('ChunkyPipes will initialize in this directory. ' +
                                  'Defaults to the user home directory.'))
        chunky_home_root = vars(parser.parse_args(command_args))['chunky-home-root']
        if chunky_home_root.lower() == 'help':
            parser.print_help()
            sys.exit(0)
        self.make_chunky_home(chunky_home_root)
