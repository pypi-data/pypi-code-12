#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'deform',
]

test_requirements = [
    'pytest',
]

setup_requirements = [
    'pytest-runner',
]

setup(
    name='deform_markdown',
    version='0.2.4',
    description="Deform widget using 'simplemde' markdown editor to edit "
                "TextArea fields.",
    long_description=readme + '\n\n' + history,
    author="Joscha Krutzki",
    author_email='joka@jokasis.de',
    url='https://github.com/liqd/deform_markdown',
    packages=[
        'deform_markdown',
    ],
    package_dir={'deform_markdown':
                 'deform_markdown'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='deform_markdown',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    setup_requires=setup_requirements,
    tests_require=test_requirements
)
