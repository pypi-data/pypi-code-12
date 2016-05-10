from setuptools import setup


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read()


setup(name='qpm',
      version=get_file_content('version.txt'),
      description='QPM is QualiSystems Package Manager',
      long_description=get_file_content('README.rst'),
      classifiers=[],
      keywords='QualiSystems',
      url='https://github.com/QualiSystems/qpm',
      author='Boris Modylevsky',
      author_email='borismod@gmail.com',
      license='Apache 2.0',
      packages=['qpm', 'qpm.packaging'],
      install_requires=[],
      test_suite='',
      tests_require=[],
      entry_points={},
      include_package_data=True,
      zip_safe=False)
