from setuptools import setup, find_packages


setup(name='logs-analyzer',
      version='0.3',
      description='Logs-analyzer is a library containing functions that can help you extract usable data from logs.',
      url='https://github.com/ddalu5/logs-analyzer',
      author='Salah OSFOR',
      author_email='osfor.salah@gmail.com',
      license='Apache V2',
      packages=find_packages(exclude=['docs', 'tests']),
      test_suite='nose.collector',
      tests_require=['nose'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Information Technology',
          'Topic :: System :: Logging',
          'Topic :: System :: Monitoring',
          'Programming Language :: Python :: 2.7',
      ],
      zip_safe=False)
