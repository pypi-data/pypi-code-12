# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
import os
import io
import re


# for getting the __version__
def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


if __name__ == '__main__':
    here = os.path.abspath(os.path.dirname(__file__))

    # Get the long description from the relevant file
    with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()

    name = "diversipy"

    setup(
        name=name,
        version=find_version(name, "__init__.py"),
        description='Sample in hypercubes, select diverse subsets, and evaluate diversity indicators',
        long_description=long_description,
        url='https://ls11-www.cs.tu-dortmund.de/people/swessing/diversipy/doc/',
        author='Simon Wessing',
        author_email='simon.wessing@tu-dortmund.de',
        license='BSD',
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',

            "Intended Audience :: Science/Research",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Mathematics",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",

            'License :: OSI Approved :: BSD License',

            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
        ],
        keywords='diversity uniformity discrepancy distance hypercube subset doe dace space-filling design experiments',
        #packages=["diversipy"],
        packages=find_packages(exclude=['test']),
        install_requires=['numpy'],
        requires=['numpy']
    )
