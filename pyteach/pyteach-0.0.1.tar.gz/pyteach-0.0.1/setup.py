import os
from setuptools   import setup, find_packages
from pip.req      import parse_requirements
from pip.download import PipSession


# import the data inside package/info.py file, without trigger the
#  importing of the whole package.
#  equivalent to the python2 execfile routine.
INFO_FILE = 'pyteach/info.py'
with open(INFO_FILE) as fd:
    code = compile(fd.read(), INFO_FILE, 'exec')
    local_vars = {}
    exec(code, {}, local_vars)  # don't use global vars, save local_vars
    __pkg_name__ = local_vars['__pkg_name__']  # save the interesting data
    __pkg_version__ = local_vars['__pkg_version__']


# access to the file at the package top level (like README)
def path_to(filename):
    return os.path.join(os.path.dirname(__file__), filename)

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(path_to('requirements.txt'),
                                  session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name = __pkg_name__,
    version = __pkg_version__,
    packages = find_packages(),
    include_package_data = True,  # read the MANIFEST.in file
    install_requires = reqs,

    author = "lucas bourneuf",
    author_email = "lucas.bourneuf@openmailbox.org",
    description = "library for teaching help",
    long_description = open(path_to('README.md')).read(),
    keywords = "mail unittest teaching automatization",
    url = "https://github.com/Aluriak/pyteach",

    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
