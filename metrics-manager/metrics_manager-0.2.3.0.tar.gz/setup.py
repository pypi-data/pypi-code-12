from distutils.core import setup

# Read the version number
with open("metrics_manager/_version.py") as f:
    exec(f.read())

setup(
    name='metrics_manager',
    version=__version__, # use the same version that's in _version.py
    author='David N. Mashburn',
    author_email='david.n.mashburn@gmail.com',
    packages=['metrics_manager'],
    scripts=[],
    url='http://pypi.python.org/pypi/metrics_manager/',
    license='LICENSE.txt',
    description='Generic system for defining, handling, storing, and loading metrics',
    long_description=open('README.txt').read(),
    install_requires=['numpy>=1.0',
                      'np_utils>=0.4.4',
                      'toposort>=1.4',
                     ],
)
