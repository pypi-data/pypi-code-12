from setuptools import setup

from distutils.command.install import install, Command
from test.test_support import run_unittest
import os,sys, unittest

sys.path.append(os.path.join(os.getcwd(), 'src'))

available_modules = ['unfolding', 'math_utils', 'plotting_utils', 'all']
help_text = 'Please specify one of: '
for module in available_modules:
    help_text += ", '%s'" % module


mods_to_test    = []
mods_to_require = []
mods_to_install = []

class InstallCommand(install):

    description = "Installs the survey_utils package; allows specification of modules to include."

    # Add your new user options to the
    # ones that are baked into the install
    # command by default. Each new CLI option
    # is a triplet:
    #
    #   long_name, short_name, help_text
    #
    # Add a '=' after the long name if the
    # option requires an argument. Use None
    # if you don't want to allow a short option.
    #
    user_options = [
        ('module=', 'm', help_text),
    ] + install.user_options

    def initialize_options(self):
        install.initialize_options(self)
        # *Must* initialize any options you introduced
        # in user_options. Else parent's finalize_options
        # won't read the option from the command line at
        # all!!!!
        self.module = None

    def finalize_options(self):
        install.finalize_options(self)
        
        assert self.module in [None] + available_modules, help_text
        
    def run(self):
        
            
        if self.module not in available_modules:
            # No module arg given on the command line.
            # Require it for the install command, so that
            # user doesn't unexpectedly install all of
            # numpy/scipy:
         
            print(help_text + '. Install aborted.')
            sys.exit()        
        
        # Install math_utils only if explicitly
        # requested in the -m/--module option,
        # or if 'all' is requested
        mods_to_install = []
        mods_to_require = []
        if self.module in ['unfolding', 'all']:
            mods_to_require.append('ordered-set>=2.0.1')
            mods_to_install.append('unfolding')
        if self.module in ['math_utils', 'all']:
            mods_to_install.append('math_utils')
            mods_to_require.extend(['scipy>=0.17.0',
                                    'pandas>=0.17.1',
                                    'freetype-py>=1.0.2',
                                    ])
        if self.module in ['plotting_utils', 'all']:
            mods_to_install.append('plotting_utils')
            mods_to_require.append('matplotlib>=1.5.0')
        install.run(self)


class TestCommand(Command):

    description = "The the survey_utils; allows specification of module to include"

    # Add these new user options to the
    # ones that are baked into the install
    # command by default:
    
    user_options = [
        ('module=', 'm', help_text),
    ] + install.user_options

    def initialize_options(self):
        # *Must* initialize any options you introduced
        # in user_options. Else parent's finalize_options
        # won't read the option from the command line at
        # all!!!!
        self.module = None

    def finalize_options(self):
        assert self.module in [None] + available_modules, help_text
        
    def run(self):

            
        if self.module not in available_modules:
            # No modules arg given on the command line.
            # Require it for the test command, so that
            # user doesn't unexpectedly install all of
            # numpy/scipy:
         
            print(help_text + ". Test aborted.")
            sys.exit()
        mods_to_test = []
        if self.module in ['unfolding', 'all']:
            from survey_utils.unfolding_test import TestUnfolding
            mods_to_test.append(TestUnfolding)
        if self.module in ['math_utils' , 'all']:
            from survey_utils.math_utils_test import TestMathUtils
            mods_to_test.append(TestMathUtils)
        if self.module in ['plotting_utils' , 'all']:
            from survey_utils.plotting_utils_test import TestPlotting
            mods_to_test.append(TestPlotting)
        
        for test_class in mods_to_test:
            run_unittest(unittest.makeSuite(test_class))


#*****test_requirements = ['nose>=1.0'] 
test_requirements = ['ordered-set>=2.0.1']
 

setup(
    name = "survey_utils",
    version = "0.0.1",
    py_modules = mods_to_install,
    cmdclass = {
      'install': InstallCommand,
      'test': TestCommand
      },

    # Dependencies on other packages:
    setup_requires   = ['nose>=1.3.7',
            #'numpy>=1.11.0'
            ],
    tests_require    = test_requirements,
    install_requires = mods_to_require + test_requirements,

    # Unit tests; they are initiated via 'python setup.py test'
    test_suite       = 'nose.collector', 

    package_dir = {'':'src'},

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
     #   '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
     #   'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Andreas Paepcke",
    author_email = "paepcke@cs.stanford.edu",
    description = "Utilities for managing survey results.",
    license = "BSD",
    keywords = "surveys, table shaping",
    url = "https://github.com/paepcke/survey_utils",   # project home page, if any
)
