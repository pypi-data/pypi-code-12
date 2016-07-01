from assemble import get_package

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

if __name__ == "__main__":
    package.setup(keywords, classifiers)
