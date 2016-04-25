from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open


def get_requirements():
    """Simply read the requirements.txt file and returns the list of the dependencies.
    :returns: list of requirements
    """
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    return requirements


reqs = get_requirements()

setup(
        name='pentaho-rest-api',

        # Versions should comply with PEP440.  For a discussion on single-sourcing
        # the version across setup.py and the project code, see
        # https://packaging.python.org/en/latest/single_source_version.html
        version='1.0.4',

        include_package_data=True,

        package_data={
            # If any package contains *.txt or *.rst files, include them:
            '': ['*.txt', '*.md'],
        },

        description='Python library for the pentaho BA REST API',
        long_description='Python library for the pentaho BA REST API',

        # The project's main homepage.
        url='git@github.com:AlayaCare/pentaho-rest-api.git',

        # Author details
        author='Saqib Khalil Yawar',
        author_email='saqib.yawar@alayacare.com',

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'Programming Language :: Python :: 2.7',
            'License :: OSI Approved :: GNU General Public License (GPL)'
        ],

        # What does your project relate to?
        keywords='pentaho rest api development',

        packages=find_packages(exclude=['contrib', 'docs', 'tests']),

        install_requires=reqs,

        extras_require={
            'dev': reqs,
            'test': reqs,
        },

        # entry_points={
        #     'console_scripts': [
        #         'users_api=pentaho-rest-api.scripts.info:info',
        #     ],
        # },
)
