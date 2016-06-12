########################################################
# Started Logging At: 2016-03-22 03:42:02
########################################################

import pyspeckit
sp = pyspeckit.Spectrum('hr2421.fit')
sp.plotter()
import specutils
specutils.io.read_fits.read_fits_spectrum1d('hr2421.fit')
x = specutils.io.read_fits.read_fits_spectrum1d('hr2421.fit')
type(x)
get_ipython().magic('run ~/repos/astropy-regions/regions/io/ds9.py')
get_ipython().magic('pwd ')
from astroquery.simbad import Simbad
Simbad.list_votable_fields()
