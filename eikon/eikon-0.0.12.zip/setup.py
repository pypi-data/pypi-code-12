from setuptools import setup, find_packages

setup(name='eikon',
      version='0.0.12',
      description='Python package for retrieving Eikon data.',
      long_description='Python package for retrieving Eikon data.',
      url='https://developers.thomsonreuters.com/tr-eikon-scripting-apis/python-thin-library-pyeikon/',
      author='Thomson Reuters',
      author_email='',
      license='MIT',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      use_2to3=True,
      zip_safe=False,
      install_requires=['requests',
                        'pandas>=0.17.0',
                        'numpy>=1.10.0',
                        'appdirs',
                        'python-dateutil',
                        'websocket-client'],
      # dependency_links => use to list dependencies not available on pypi platform
      test_suite='test',
      test_require=['nose', 'mock', 'lettuce'])
