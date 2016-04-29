import sys
import bookbank

from setuptools import setup, find_packages

try:
    from pip.req import parse_requirements
except ImportError:
    sys.stderr.write("Please install pip by running: easy_install pip")
    sys.exit(-1)

# Load metadata
with open('README.md', 'r') as fh:
    readme_contents = fh.read()

# read pip requirements
pip_requires = parse_requirements('requirements.txt', session=False)
install_reqs = [str(ir.req) for ir in pip_requires]


setup(
    name = bookbank.__name__,
    version = bookbank.__version__,

    packages = find_packages(),
    scripts = ['bb.py'],
    install_requires = install_reqs,

    author = 'nikcub',
    author_email = 'nikcub@gmail.com',
    description = bookbank.__desc__,
    long_description = readme_contents,
    license = 'MIT',
    keywords = ['ebook', 'book'],
    url = 'https://www.github.com/bookbank/bookbank',

    classifiers = [
        'Development Status :: 3 - Alpha',
    ]
)