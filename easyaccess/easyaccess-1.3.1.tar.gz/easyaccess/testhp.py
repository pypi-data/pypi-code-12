import numpy as np
from eautils.fun_utils import toeasyaccess


@toeasyaccess
def ang2hpix(ra,dec, nside=1024):
    """
    Convert from ra, dec to hpix indices
    """
    phi = ra/180.*np.pi
    theta = (90. - dec)/180.*np.pi
    nside = int(nside)
    if nest == 'True' :
        nest = True
    else:
        nest = False
    pixs = np.ang2pix(nside, theta, phi, nest=True)
    return pixs

@toeasyaccess
def ang2hpix2(ra,dec, nside=1024, d=1,c=2,f=3,r=4):
    """
    Convert from ra, dec to hpix indices
    """
    phi = ra/180.*np.pi
    theta = (90. - dec)/180.*np.pi
    nside = int(nside)
    if nest == 'True' :
        nest = True
    else:
        nest = False
    pixs = np.ang2pix(nside, theta, phi, nest=True)
    return pixs
