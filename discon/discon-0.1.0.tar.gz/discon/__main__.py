#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""
Push project to pypi and binstar (Anaconda)


"""

import logging

logger = logging.getLogger(__name__)
import argparse
import subprocess
import os
import os.path as op
import shutil
import glob

def make(args):
    if not op.exists("build.sh"):
        with open('build.sh', 'a') as the_file:
            the_file.write('#!/bin/bash\n\n$PYTHON setup.py install\n')
    if not op.exists("bld.bat"):
        with open('bld.bat', 'a') as the_file:
            the_file.write('"%PYTHON%" setup.py install\nif errorlevel 1 exit 1')

    if (args.action == "patch"):
        print "pull, patch, push, push --tags"
        subprocess.call("git pull", shell=True)
        subprocess.call("bumpversion patch", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git push --tags", shell=True)
    elif (args.action == "minor"):
        print "pull, patch, push, push --tags"
        subprocess.call("git pull", shell=True)
        subprocess.call("bumpversion minor", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git push --tags", shell=True)
    elif (args.action == "major"):
        print "pull, patch, push, push --tags"
        subprocess.call("git pull", shell=True)
        subprocess.call("bumpversion major", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git push --tags", shell=True)
    elif (args.action == "stable"):
        subprocess.call("git push --tags", shell=True)
        subprocess.call("git checkout stable", shell=True)
        subprocess.call("git pull origin master", shell=True)
        subprocess.call("git push", shell=True)
        subprocess.call("git checkout master", shell=True)
        return
    elif (args.action == "init"):
        init(args.initprojectname)
        return
# fi
    # upload to pypi


    logger.debug("pypi upload")
    subprocess.call(["python", "setup.py", "register", "sdist", "upload"])

    # build conda and upload
    logger.debug("conda clean")

    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

    # this fixes upload confilct
    dr = glob.glob("dist/*.tar.gz")
    for onefile in dr:
        os.remove(onefile)

    # try:
    #     subprocess.call(["rm ", "-rf ", "win-*"])
    # except OSError:
    #     pass
    # try:
    #     subprocess.call(["rm ", "-rf ", "linux-*"])
    # except OSError:
    #     pass
    # try:
    #     subprocess.call(["rm ", "-rf ", "osx-*"])
    # except OSError:
    #     pass
    # # this fixes upload confilct
    # try:
    #     subprocess.call(["rm ", "-rf ", "dist/*.tar.gz"])
    # except OSError:
    #     pass

    logger.debug("conda build")

    # subprocess.call("conda build -c mjirik -c SimpleITK .", shell=True)
    subprocess.call(["conda", "build", "."])
    output_name_lines = subprocess.check_output(["conda", "build", "--output", "."])
    # get last line of output
    output_name = output_name_lines.split("\n")[-2]
    subprocess.call(["conda", "convert", "-p", "all", output_name])

    logger.debug("binstar upload")
    # it could be ".tar.gz" or ".tar.bz2"
    subprocess.call("binstar upload */*.tar.*z*", shell=True)

    logger.debug("rm files")
    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

def init(project_name="project_name"):
    _SETUP_PY = """# Fallowing command is used to upload to pipy
#    python setup.py register sdist upload
from setuptools import setup, find_packages
# Always prefer setuptools over distutils
from os import path

here = path.abspath(path.dirname(__file__))
setup(
    name='{}',
    description='distribution to pypi and conda',
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.0',
    url='https://github.com/mjirik/{}',
    author='Miroslav Jirik',
    author_email='miroslav.jirik@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='dicom 3D read write',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['dist',  'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=['numpy', 'conda'],
    # 'SimpleITK'],  # Removed becaouse of errors when pip is installing
    dependency_links=[],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={{
    #     'sample': ['package_data.dat'],
    # }},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={{
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # }},
)
"""

    _SETUP_CFG = """
[bumpversion]
current_version = 0.0.0
files = setup.py meta.yaml
commit = True
tag = True
tag_name = {new_version}

[nosetests]
attr = !interactive,!slow,!LAR
"""

    _META_YML = """package:
  name: {}
  version: "0.0.0"

source:
# this is used for build from git hub
  git_rev: 0.0.0
  git_url: https://github.com/mjirik/{}.git

# this is used for pypi
  # fn: io3d-1.0.30.tar.gz
  # url: https://pypi.python.org/packages/source/i/io3d/io3d-1.0.30.tar.gz
  # md5: a3ce512c4c97ac2410e6dcc96a801bd8
#  patches:
   # List any patch files here
   # - fix.patch

# build:
  # noarch_python: True
  # preserve_egg_dir: True
  # entry_points:
    # Put any entry points (scripts to be generated automatically) here. The
    # syntax is module:function.  For example
    #
    # - io3d = io3d:main
    #
    # Would create an entry point called io3d that calls io3d.main()


  # If this is a new build for the same version, increment the build
  # number. If you do not include this key, it defaults to 0.
  # number: 1

requirements:
  build:
    - python
    - setuptools

  run:
    - python
    - conda-build
    - anaconda-client

test:
  # Python imports
  imports:
    - {}

  # commands:
    # You can put test commands to be run here.  Use this to test that the
    # entry points work.


  # You can also put a file called run_test.py in the recipe that will be run
  # at test time.

  # requires:
    # Put any additional test requirements here.  For example
    # - nose

about:
  home: https://github.com/mjirik/disco
  license: BSD License
  summary: 'distribution to pypi and conda'

# See
# http://docs.continuum.io/conda/build.html for
# more information about meta.yaml
"""


    _CONDARC = """#!/bin/bash

$PYTHON setup.py install

# Add more build steps here, if they are necessary.

# See
# http://docs.continuum.io/conda/build.html
# for a list of environment variables that are set during the build process.
"""
    if not op.exists(".condarc"):
        with open('.condarc', 'a') as the_file:
            the_file.write('channels:\n  - default\n#  - mjirik')
    if not op.exists("setup.py"):
        with open('setup.py', 'a') as the_file:
            the_file.write(_SETUP_PY.format(project_name, project_name))
    if not op.exists("setup.cfg"):
        with open('setup.cfg', 'a') as the_file:
            the_file.write(_SETUP_CFG)
    if not op.exists("meta.yml"):
        with open('meta.yml', 'a') as the_file:
            the_file.write(_META_YML.format(project_name, project_name, project_name))


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "action",
        help="Available values are: 'init', 'patch', 'minor', 'major' or 'stable'",
        default=None)
    parser.add_argument(
        "initprojectname",
        nargs='?',
        help="set project name in generated files if 'init' action is used",
        default="default_project")
    # parser.add_argument(
    #     "arg2",
    #     required=False,
    #     default=None)
    # parser.add_argument(
    #     '-i', '--inputfile',
    #     default=None,
    #     # required=True,
    #     help='input file'
    # )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    args = parser.parse_args()

    if args.debug:
        ch.setLevel(logging.DEBUG)

    make(args)


if __name__ == "__main__":
    main()

