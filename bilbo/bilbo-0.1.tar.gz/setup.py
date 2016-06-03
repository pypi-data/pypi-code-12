from setuptools import setup, find_packages
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/bilbo/__version__.py").read())


def readme():
    with open(moduleDirectory + '/README.rst') as f:
        return f.read()


setup(name="bilbo",
      version=__version__,
      description="Commands to help build and maintain a gollum wiki",
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      keywords=['tool, wiki'],
      url='https://github.com/thespacedoctor/bilbo',
      download_url='https://github.com/thespacedoctor/bilbo/archive/v%(__version__)s.zip' % locals(
      ),
      author='David Young',
      author_email='davidrobertyoung@gmail.com',
      license='MIT',
      packages=find_packages(),
      package_data={'bilbo': [
          'resources/*/*', 'resources/*.*']},
      install_requires=[
          'pyyaml',
          'bilbo'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      # entry_points={
      #     'console_scripts': ['bilbo=bilbo.cl_utils:main'],
      # },
      zip_safe=False)
