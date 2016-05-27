#!/usr/bin/env python
from setuptools import setup
import versioneer


desc = """
RADsim: simulate reduced-represention sequencing platforms based on restriction
digestion, including RADseq and GBS.
"""

setup_requires = [
    'pytest-runner',
]

with open('requirements.txt') as fh:
    install_requires = [req.strip() for req in fh]

test_requires = [
    'pep8',
    'pylint',
    'pytest',
]

command_classes = versioneer.get_cmdclass()

setup(
    name="radsim",
    packages=['radsim', ],
    version=versioneer.get_version(),
    entry_points={
        'console_scripts': [
            'radsim-hist = radsim.main:hist_main',
            'radsim-digest = radsim.main:digest_main',
            'radsim-rebed = radsim.main:rebed_main',
        ],
    },
    cmdclass=command_classes,
    install_requires=install_requires,
    tests_require=test_requires,
    setup_requires=setup_requires,
    description=desc,
    author="Kevin Murray",
    author_email="spam@kdmurray.id.au",
    url="https://github.com/kdmurray91/radhax",
    keywords=[
        "bioinformatics",
        "RADseq",
        "GBS",
        "Genotyping by Sequencing",
        "Next-gen Sequencing",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
    ],
)
