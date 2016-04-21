from setuptools import setup




setup(name='iitg_acad_hub',
      version='2.3.1',
      description='Acad Hub for IIT Guwahati',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
      ],
      keywords='acad hub iitg iit books pdf lend ',
      author='team10cs243',
      license='GPLv3',
      packages = ['iitg_acad_hub'],
      package_data={'iitg_acad_hub':['*.py','*.txt','icon/*'],},
      install_requires=[
          'requests','beautifulsoup4'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      entry_points={
          'console_scripts': ['acadHub=iitg_acad_hub.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)