from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import os
import re
import sys

v = open(os.path.join(os.path.dirname(__file__), 'choco', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

if sys.version_info < (2, 6):
    raise Exception("Choco requires Python 2.6 or higher.")

markupsafe_installs = (
    sys.version_info >= (2, 6) and sys.version_info < (3, 0)
) or sys.version_info >= (3, 3)

install_requires = []

if markupsafe_installs:
    install_requires.append('MarkupSafe>=0.9.2')

try:
    import argparse
except ImportError:
    install_requires.append('argparse')


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='Choco',
      version=VERSION,
      description="A super-fast templating language that borrows the \
 best ideas from the existing templating languages.",
      long_description=readme,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='templates',
      author='Thomas',
      author_email='lyanghwy@gmail.com',
      url='https://github.com/whiteclover/Choco',
      license='MIT',
      packages=find_packages('.', exclude=['examples*', 'test*']),
      tests_require=['pytest', 'mock'],
      cmdclass={'test': PyTest},
      zip_safe=False,
      install_requires=install_requires,
      extras_require={},
      entry_points="""
      [python.templating.engines]
      choco = choco.ext.turbogears:TGPlugin

      [pygments.lexers]
      choco = choco.ext.pygmentplugin:ChocoLexer
      html+choco = choco.ext.pygmentplugin:ChocoHtmlLexer
      xml+choco = choco.ext.pygmentplugin:ChocoXmlLexer
      js+choco = choco.ext.pygmentplugin:ChocoJavascriptLexer
      css+choco = choco.ext.pygmentplugin:ChocoCssLexer

      [babel.extractors]
      choco = choco.ext.babelplugin:extract

      [lingua.extractors]
      choco = choco.ext.linguaplugin:LinguaChocoExtractor

      [console_scripts]
      choco-render = choco.cmd:cmdline
      """
)
