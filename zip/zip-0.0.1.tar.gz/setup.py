from setuptools import setup
import zip
from os import path
from pip.req import parse_requirements

here = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    with open(path.join(here, 'README.md')) as f:
        long_description = f.read()

install_requires = [str(ir.req)
                    for ir in parse_requirements(
                        path.join(here, 'requirements.txt'),
                        session=False)]

setup(
    name=zip.__title__,
    version=zip.__version__,
    description=zip.__summary__,
    long_description=long_description,
    license=zip.__license__,
    url=zip.__uri__,
    author=zip.__author__,
    author_email=zip.__email__,
    packages=["zip"],
    entry_points={
        "console_scripts": [
            "iou = zip.run:main",
        ],
    },
    install_requires=install_requires,
)

