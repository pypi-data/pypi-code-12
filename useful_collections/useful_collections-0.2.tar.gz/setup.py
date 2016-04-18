from setuptools import setup, find_packages
from codecs import open
from os import path
from pip.req import parse_requirements

here = path.abspath(path.dirname(__file__))

# read requirements.txt of production
setup_dir = path.dirname(path.realpath(__file__))

def env_requirements(env_name):
    _parsed_reqs = parse_requirements(
        path.join(setup_dir, 'requirements/%s.txt' % env_name),
        session=False)
    return [str(ir.req) for ir in _parsed_reqs]

setup(
    name='useful_collections',
    version='0.2',
    author='Samuel Sampaio',
    author_email='samuel@smk.net.br',
    description='Useful collections for manipulate data in Python',
    url='https://github.com/samukasmk/python-useful-collections',
    download_url = 'https://github.com/samukasmk/python-useful-collections/tarball/0.1', # I'll explain this in a second
    keywords = ['collections', 'dict', 'immutable', 'immutability', 'lock',
                'data', 'modules', 'class'],
    # packages of project
    packages=find_packages(exclude=[
            'contrib', 'docs', 'tests*','samples', 'requirements']),


    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # install_requires=env_requirements('prod'),

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': env_requirements('dev'),
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'sample': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },

    license='Apache2',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',


        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',

        # Topics
        'Topic :: Utilities'
    ],
)
