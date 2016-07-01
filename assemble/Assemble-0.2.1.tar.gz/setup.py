from os import path
import sys

sys.path.insert(0, path.join(path.dirname(__file__), 'src'))
from assemble import get_package  # flake8: noqa

package = get_package()

keywords = [
    "routing"
]
classifiers = [
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",

    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: Implementation :: CPython",

    "Topic :: Software Development :: Libraries :: Python Modules",
]

entry_points = '''
    [console_scripts]
    assemble=assemble.cli:main
'''

if __name__ == "__main__":
    package.setup(keywords, classifiers, entry_points=entry_points)
