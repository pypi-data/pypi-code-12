import os
import shutil

import sh
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ievv_opensource.ievvtasks_common.open_file import open_file_with_default_os_opener
from ievv_opensource.utils import virtualenvutils


class Command(BaseCommand):
    help = 'Build, open and clean docs (or all at once).'

    def __get_documentation_directory(self):
        default_directory = os.path.join('not_for_deploy', 'docs')
        return getattr(settings, 'IEVVTASKS_DOCS_DIRECTORY', default_directory)

    def __get_documentation_build_directory(self):
        default_build_directory = os.path.join(self.__get_documentation_directory(), '_build')
        return getattr(settings, 'IEVVTASKS_DOCS_BUILD_DIRECTORY', default_build_directory)

    def __get_dash_documentation_name(self):
        name = getattr(settings, 'IEVVTASKS_DOCS_DASH_NAME', None)
        if name:
            return name
        else:
            raise AttributeError('--dash requires the IEVVTASKS_DOCS_DASH_NAME setting.')

    def __get_documentation_indexhtml_path(self):
        return os.path.join(self.__get_documentation_build_directory(), 'index.html')

    def add_arguments(self, parser):
        parser.add_argument('-b', '--build', dest='build_docs',
                            required=False, action='store_true',
                            help='Build the docs.')
        parser.add_argument('-c', '--clean', dest='cleandocs',
                            required=False, action='store_true',
                            help='Remove any existing built docs before building the docs.')
        parser.add_argument('-o', '--open', dest='opendocs',
                            required=False, action='store_true',
                            help='Open the docs after building them.')
        parser.add_argument('--dash', dest='doc2dash',
                            required=False, action='store_true',
                            help='Add the docs to Dash with doc2dash. Install doc2dash with ``pip install doc2dash``.')
        parser.add_argument('--fail-on-warning', dest='fail_on_warning',
                            required=False, action='store_true',
                            help='Fail on warning.')

    def handle(self, *args, **options):
        cleandocs = options['cleandocs']
        build_docs = options['build_docs']
        opendocs = options['opendocs']
        doc2dash = options['doc2dash']
        self.indexhtmlpath = self.__get_documentation_indexhtml_path()
        self.fail_on_warning = options['fail_on_warning']

        if not (cleandocs or opendocs or build_docs or doc2dash):
            raise CommandError('You must specify at least one of: --build, '
                               '--clean, --open or --dash. See --help for more info.')

        if cleandocs and opendocs and not build_docs:
            raise CommandError('Can not use --clean and --open without also using --build.')

        virtualenvutils.add_virtualenv_bin_directory_to_path()
        if cleandocs:
            self.__cleandocs()
        if build_docs:
            self.__build_docs()
        if opendocs:
            self._opendocs()
        if doc2dash:
            self.__doc2dash()

    def _opendocs(self):
        self.stdout.write('Opening {} in your browser.'.format(self.indexhtmlpath))
        open_file_with_default_os_opener(self.indexhtmlpath)

    def __doc2dash(self):
        doc2dash_command = sh.Command('doc2dash')
        kwargs = {
            'A': True,  # Add to global dash
            'f': True,  # Overwrite existing
            'name': self.__get_dash_documentation_name()
        }
        try:
            doc2dash_command(self.__get_documentation_build_directory(),
                             _out=self.__print_stdout,
                             _err=self.__print_stderr,
                             **kwargs)
        except sh.ErrorReturnCode:  # pragma: no cover
            # We do not need to show any more errors here - they
            # have already been printed by the _out and _err handlers.
            # Excluded from code coverage because we do not test fail_on_warning
            # as explained above.
            pass
        else:
            self.stdout.write('Built dash docs.')

    def __cleandocs(self):
        if os.path.exists(self.__get_documentation_build_directory()):
            self.stdout.write('Removing {}'.format(self.__get_documentation_build_directory()))
            shutil.rmtree(self.__get_documentation_build_directory())
        else:  # pragma: no cover
            # Excluded from code coverage because this does not happen
            # since we always run tests with a removed build directory.
            self.stdout.write('Not removing {} - it does not exist.'.format(
                self.__get_documentation_build_directory()))

    def __print_stdout(self, line):
        self.stdout.write(line.rstrip())

    def __print_stderr(self, line):
        self.stderr.write(line.rstrip())

    def __build_docs(self):
        sphinx_build_html = sh.Command('sphinx-build')
        kwargs = {
            'b': 'html'
        }
        if self.fail_on_warning:  # pragma: no cover
            # Excluded from coverage because testing this would
            # require a complete mock of the docs directory.
            kwargs['W'] = True
            kwargs['T'] = True
        try:
            sphinx_build_html(self.__get_documentation_directory(),
                              self.__get_documentation_build_directory(),
                              _out=self.__print_stdout,
                              _err=self.__print_stderr,
                              **kwargs)
        except sh.ErrorReturnCode:  # pragma: no cover
            # We do not need to show any more errors here - they
            # have already been printed by the _out and _err handlers.
            # Excluded from code coverage because we do not test fail_on_warning
            # as explained above.
            pass
        else:
            self.stdout.write('Built docs. Use ``ievv docs -o`` to open them in your browser to view them.')
