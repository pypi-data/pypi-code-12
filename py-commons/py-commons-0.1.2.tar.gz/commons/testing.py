from distutils.cmd import Command
from unittest import TestCase


class PyTest(Command):
    """
    This class can be used in setup.py to provide the ability to run tests:
    setup(
        ...
        cmdclass={'test': PyTest},
        ...
    )
    """
    description = "Run the tests with py.test framework"
    user_options = [
        ('teamcity', None, 'Enable teamcity support (requires teamcity-messages package)')
    ]

    def initialize_options(self):
        self.teamcity = None

    def finalize_options(self):
        if self.teamcity:
            try:
                import teamcity
            except ImportError:
                raise ImportError('--teamcity option requires teamcity-messages package installed')

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call(
            [sys.executable, 'runtests.py'] +
            (['--teamcity'] if self.teamcity else [])
        )
        raise SystemExit(errno)