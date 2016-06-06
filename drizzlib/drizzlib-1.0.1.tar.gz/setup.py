import numpy

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

# Read the version number from the VERSION file
from os.path import abspath, dirname, join

with open(join(dirname(abspath(__file__)), 'VERSION'), 'r') as version_file:
    version = version_file.read().strip()

# Set up our C extension
optimized_module = Extension(
    'optimized',
    sources=[
        'src/optimized.c',
    ],
    include_dirs=[numpy.get_include()]
)

setup(
    name='drizzlib',
    version=version,
    author='Paradis Deborah',
    author_email='deborah.paradis@irap.omp.eu',
    maintainer='Antoine Goutenoir',
    maintainer_email='antoine.goutenoir@irap.omp.eu',
    url='https://gitlab.irap.omp.eu/OV-GSO-DC/drizzlib',
    license='GPL',
    description="Drizzlib is a drizzling module to convert from HEALPIX to "
                "WCS FITS files.",
    ext_modules=[optimized_module],
    requires=['numpy', 'astropy', 'healpy'],
    packages=['drizzlib'],
    package_dir={'drizzlib': 'lib'},
    provides=['drizzlib'],
    scripts=['bin/healpix2wcs']
)
