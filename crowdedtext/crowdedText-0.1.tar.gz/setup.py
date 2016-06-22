from setuptools import setup, find_packages
import os

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/crowdedText/__version__.py").read())


def readme():
    with open(moduleDirectory + '/README.rst') as f:
        return f.read()


setup(name="crowdedText",
      version=__version__,
      description="A small library for automatically adjusting text position in matplotlib plots to minimize overlaps (forked and modified from Phlya's adjustText)",
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      keywords=['matplotlib'],
      url='https://github.com/thespacedoctor/crowdedText',
      download_url='https://github.com/thespacedoctor/crowdedText/archive/v%(__version__)s.zip' % locals(
      ),
      author='David Young',
      author_email='davidrobertyoung@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'pyyaml',
          'crowdedText',
          'fundamentals'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      # entry_points={
      #     'console_scripts': ['crowdedText=crowdedText.cl_utils:main'],
      # },
      zip_safe=False)
