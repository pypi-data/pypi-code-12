from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


setup(name='jsreport',
      version='0.2.2',
      description='Simple tool to pull basic reporting data out of JustServe (https://www.justserve.org/).',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Religion',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
          'Topic :: Other/Nonlisted Topic',
      ],
      url='https://github.com/abadstubner/JustServe_Reports',
      author='abadstubner',
      author_email='andrew+pypi@badstubner.com',
      license='MIT',
      packages=['jsreport'],
      install_requires=[
          'selenium',
      ],
      zip_safe=False)
