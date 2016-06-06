from kapteyn import wcs
from numpy import nan

dec0 = 89.9999999999
mu = 2.0; phi = 180.0; theta = 60
header = {'NAXIS' : 2, 'NAXIS1': 100, 'NAXIS2': 80,
         'CTYPE1' : 'RA---SZP',
         'CRVAL1' : 0.0, 'CRPIX1' : 50, 'CUNIT1' : 'deg', 'CDELT1' : -4.0,
         'CTYPE2' : 'DEC--SZP',
         'CRVAL2' : dec0, 'CRPIX2' : 20, 'CUNIT2' : 'deg', 'CDELT2' : 4.0,
         'PV2_1'  : mu, 'PV2_2'  : phi, 'PV2_3' : theta,
        }

proj = wcs.Projection(header)
w = (180, -30)
p = (nan, nan)
print proj.topixel(w)              # Dit werkt wel
wor, pix = proj.mixed(w, p)   # Werkt niet wegens "Success". Zie Exception
print wor, pix

