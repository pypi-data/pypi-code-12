from distutils.core import setup
from setuptools import find_packages
from libaws.base import platform

install_requires = ['boto3','pyyaml']

if platform.CURRENT_OS_SYSTEM == platform.LINUX_OS_SYSTEM:
    install_requires.append('termcolor')

try:
    import argparse     # NOQA
except ImportError:
    install_requires.append('argparse')

setup(name='libaws',
        version='1.0.4',
        description='''libaws is a program can implement amason web service ,such as download files from bucket
             and upload multipart files to bucket etc, which support resume from break point and create instance vpc subet etc from config file''',
        author='wukan',
        author_email='kan.wu@gengtalks.com',
        url='https://gitlab.com/wekay102200/genetalk_libaws.git',
        license='Genetalks',
        packages=find_packages(),
#        include_package_data=False,
        install_requires=install_requires,
        zip_safe=False,
        test_suite='libaws.tests',
#        package_dir={
 #           'libaws': 'libaws',
  #      },
        package_data={'libaws': [
                    'demo/*yaml',
                    'demo/bucket_policy.json',
                    'ec2/data/default*.yaml',
        ]},
        classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
        ],
        entry_points="""
        [console_scripts]
        awskit = libaws.awskit:main
        """
)
