from setuptools import setup
import sys
import psst
from os import path

here = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    with open(path.join(here, 'README.md')) as f:
        long_description = f.read()

from pip.req import parse_requirements
install_requires = [str(ir.req) for ir in parse_requirements(path.join(here, 'requirements.txt'), session=False)]

setup(
    name=psst.__title__,
    version=psst.__version__,

    description=psst.__summary__,
    long_description=long_description,
    license=psst.__license__,
    url=psst.__uri__,

    author=psst.__author__,
    author_email=psst.__email__,

    packages=["psst"],

    entry_points={
        "console_scripts": [
            "psst = psst.run:main",
        ],
    },

    install_requires=install_requires,

    # dependency_links=[
        # "git+ssh://git@github.com/kdheepak89/click.git@7.0#egg=click-7.0"
    # ]
)

