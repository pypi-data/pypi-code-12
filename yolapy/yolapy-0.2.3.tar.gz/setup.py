from setuptools import find_packages, setup

import yolapy


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.rst') as changelog_file:
    changelog = changelog_file.read()

setup(
    name='yolapy',
    version=yolapy.__version__,
    description='Python client for the Yola API',
    long_description='%s\n\n%s' % (readme, changelog),
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url='https://github.com/yola/yolapy',
    packages=find_packages(),
    test_suite='nose.collector',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'demands >= 1.1.0, < 2.0.0',
        'six >= 1.9.0, < 1.10.0',
    ],
    tests_require=[
        'nose >= 1.3.0, < 1.4.0',
    ],
)
