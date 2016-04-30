import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

data_files = [
    (root, [os.path.join(root, f) for f in files])
        for root, dirs, files in os.walk('examples')
]

setup(
    name='slack-groupmgr',
    version='1.0.2',
    description="manage private group membership",
    long_description=long_description,
    url='https://gitlab.com/pleasantone/slack-groupmgr',

    author='Paul Traina',
    author_email='bulk+pypi@pst.org',

    packages=find_packages(exclude=['examples', 'tests']),
    entry_points = {
        'console_scripts': [
            'groupmgr=slack_groupmgr.cmdline:main',
            'groupmgr-cgi=slack_groupmgr.cgifront:main',
            'groupmgr-flask=slack_groupmgr.flask:main'
        ]
    },
    install_requires=[
        'requests',
        'appdirs',
        'slacker',
        'jinja2',
        'Flask'
    ],
    include_package_data=True,
    package_data={
        'slack_groupmgr': ['templates/*', 'examples/*', 'static/*']
    },
    data_files=data_files,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Chat',
        'Topic :: Office/Business :: Groupware',
    ],
)
