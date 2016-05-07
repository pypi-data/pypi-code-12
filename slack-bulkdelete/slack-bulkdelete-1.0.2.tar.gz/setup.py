import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

data_files = [
    (root, [os.path.join(root, f) for f in files]) for root, dirs, files in os.walk('examples')
]

setup(
    name='slack-bulkdelete',
    version='1.0.2',
    description="keep your team under the file upload limit",
    long_description=long_description,
    url='https://gitlab.com/pleasantone/slack-bulkdelete',

    author='Paul Traina',
    author_email='bulk+pypi@pst.org',

    packages=find_packages(exclude=['examples', 'tests']),
    package_data={
        '': ['templates/*', 'examples/*', 'static/*']
    },
    data_files=data_files,
    zip_safe=False,
    install_requires=[
        'slacker',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'slack-bulkdelete=slack_bulkdelete:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Chat',
        'Topic :: Office/Business :: Groupware'
    ],
)
