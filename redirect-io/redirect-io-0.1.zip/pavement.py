import sys

from paver.easy import task, needs, path, sh, cmdopts, options
from paver.setuputils import setup, install_distutils_tasks
from distutils.extension import Extension
from distutils.dep_util import newer

sys.path.insert(0, path('.').abspath())
import version

setup(name='redirect-io',
      version=version.getVersion(),
      description='Context managers to redirect stderr or stdout.',
      keywords='stdout, stderr, context manager',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/wheeler-microfluidics/redirect-io',
      license='GPL',
      packages=['redirect_io', ],
      install_requires=[],
      # Install data listed in `MANIFEST.in`
      include_package_data=True)


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist') 
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
