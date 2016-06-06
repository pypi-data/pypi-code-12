# Read the version number from the VERSION file
from os.path import abspath, dirname, join

with open(join(dirname(abspath(__file__)), 'VERSION'), 'r') as version_file:
    __version__ = version_file.read().strip()

# Import sub functions for convenience
# That way we can use them by simply importing them like so :
# from drizzlib import healpix2wcs, wcs2healpix
from lib.healpix2wcs import healpix2wcs
from lib.wcs2healpix import wcs2healpix