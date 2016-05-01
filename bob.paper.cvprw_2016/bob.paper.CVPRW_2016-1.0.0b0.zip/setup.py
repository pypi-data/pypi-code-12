#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# Fri 29 Apr 08:18:08 2016 CEST
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#

from setuptools import setup, find_packages

# Define package version
version = open("version.txt").read().rstrip()

from bob.extension.utils import load_requirements
install_requires = load_requirements()



# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name='bob.paper.CVPRW_2016',
    version=version,
    description='Running the experiments as given in paper: "Heterogeneous Face Recognition using Inter-Session Variability Modelling".',

    url='http://gitlab.idiap.ch/',
    license='BSD',
    author='Tiago de Freitas Pereira',
    author_email='tiago.pereira@idiap.ch',
    keywords='bob',

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,

    # This line defines which packages should be installed when you "install"
    # this package. All packages that are mentioned here, but are not installed
    # on the current system will be installed locally and only visible to the
    # scripts of this package. Don't worry - You won't need adminstrative
    # privileges when using buildout.
    install_requires=install_requires,


    # This entry defines which scripts you will have inside the 'bin' directory
    # once you install the package (or run 'bin/buildout'). The order of each
    # entry under 'console_scripts' is like this:
    #   script-name-at-bin-directory = module.at.your.library:function
    #
    # The module.at.your.library is the python file within your library, using
    # the python syntax for directories (i.e., a '.' instead of '/' or '\').
    # This syntax also omits the '.py' extension of the filename. So, a file
    # installed under 'example/foo.py' that contains a function which
    # implements the 'main()' function of particular script you want to have
    # should be referred as 'example.foo:main'.
    #
    # In this simple example we will create a single program that will print
    # the version of bob.
    entry_points={

      # scripts should be declared using this entry:
      'console_scripts': [
         'ISV_intuition.py         = bob.paper.CVPRW_2016.script.ISV_intuition:main',
         'generate_plot_results.py = bob.paper.CVPRW_2016.script.generate_plot_results:main',
        ],

    },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
)
