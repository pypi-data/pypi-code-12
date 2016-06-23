# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.test import test


class custom_test(test):
    # hack to run my functional tests on buildbot
    user_options = test.user_options + [
        ('tornadoenv=', None, "run tornado on correct virtualevn"),
    ]

    def initialize_options(self):
        super(custom_test, self).initialize_options()
        self.tornadoenv = None


def get_version_from_file():
    # get version number from __init__ file
    # before module is installed

    fname = 'jaobi/__init__.py'
    with open(fname) as f:
        fcontent = f.readlines()
    version_line = [l for l in fcontent if 'VERSION' in l][0]
    return version_line.split('=')[1].strip().strip("'").strip('"')


setup(name='jaobi',
      version=get_version_from_file(),
      author='You Buddy',
      author_email='you@somewhere.com',
      description='jaobi is really cool software',
      long_description="It's based on pyrocumulus and have nice features!",
      url='https://some-url-to-my-project.com',
      packages=['jaobi', 'jaobi.commands', 'jaobi.reports'],
      include_package_data=True,
      install_requires=['pyrocumulus>=0.6.6', 'mongomotor>=0.6.1',
                        'pyzmq>=14.7.0'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
      ],
      test_suite='tests',
      provides=['jaobi'],
      cmdclass={'test': custom_test})
