from setuptools import setup
from distutils.core import setup
def readme():
 with open('README.rst')as f:
     return f.read()

setup(name='web_test',
      version='0.1',
      description='The funniest joke in the world',
      long_description=readme(),
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['web_test'],
      install_requires=[
          'markdown',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      scripts=['bin/web_test-joke'],
      entry_points={
      'console_scripts':['web_test-joke=web_test.command_line:main'],
      },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      zip_safe=False)
