from setuptools import setup, find_packages
import os
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('qtk/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


BASE_PATH = os.path.dirname(__file__)


def get_requirements(suffix=''):
    with open(os.path.join(BASE_PATH, 'Requirements%s.txt' % suffix)) as f:
        rv = f.read().splitlines()
    return rv

setup(
    name='qtk',
    version=version,
    url='https://github.com/gouthambs/qtk-python',
    license='MIT',
    author='Goutham Balaraman',
    author_email='gouthaman.balaraman@gmail.com',
    description='A QuantLib Python ToolKit',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_requirements(),
    tests_require=["nose"],
    test_suite='nose.collector',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)