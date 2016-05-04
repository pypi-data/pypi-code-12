from distutils.core import setup

# Read the version number
with open("mpl_utils/_version.py") as f:
    exec(f.read())

setup(
    name='mpl_utils',
    version=__version__, # use the same version that's in _version.py
    author='David N. Mashburn',
    author_email='david.n.mashburn@gmail.com',
    packages=['mpl_utils'],
    scripts=[],
    url='http://pypi.python.org/pypi/mpl_utils/',
    license='LICENSE.txt',
    description='plotting utilites build around matplotlib',
    long_description=open('README.txt').read(),
    install_requires=[
                      'numpy>=1.0',
                      'matplotlib>=1.0',
                      'np_utils>=0.4.1.1',
                     ],
)
