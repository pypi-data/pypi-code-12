from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def readme():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name='thriftplus',
    version='0.0.3',
    description='A compiler for ThriftPlus, which is an extension to Thrift, with better support for emitting packages and with a niftier library and import system.',
    long_description=readme(),
    keywords='thriftplus compiler thrift',
    url='http://github.com/silver-saas/thriftplus',
    author='Horia Coman',
    author_email='horia141@gmail.com',
    license='All right reserved',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    entry_points = {
        'console_scripts': [
            'thriftplus=thriftplus.thriftplus:main'
            ],
        },
    install_requires=[
        'thrift==0.9.3',
        # For testing
        'mockito==0.5.2',
        'tabletest==1.1.0',
        ],
    test_suite='tests',
    tests_require=[],
    include_package_data=True,
    zip_safe=False
)
