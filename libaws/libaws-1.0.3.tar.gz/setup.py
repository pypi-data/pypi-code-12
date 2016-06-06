from distutils.core import setup
from setuptools import find_packages
from libaws.base import platform

install_requires = ['boto3']

if platform.CURRENT_OS_SYSTEM == platform.LINUX_OS_SYSTEM:
    install_requires.append('termcolor')
setup(name='libaws',
        version='1.0.3',
        description='''libaws is a program can implement amason web service ,such as download bucket files
             and upload files to bucket etc ''',
        author='wukan',
        author_email='kan.wu@gengtalks.com',
        url='https://gitlab.com/wekay102200/genetalk_libaws.git',
        license='Genetalks',
        packages=find_packages(),
        include_package_data=True,
        install_requires=install_requires,
        zip_safe=False,
     #   package_dir={
      #      'awslib': 'awslib',
       # },
       #package_data={'awslib': ['common/logger111.conf']},
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
        ]
)
