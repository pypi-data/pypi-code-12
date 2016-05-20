import numpy as np
import pandas as pd
from astropy.io import fits

def fits2df(filename):
    hdulist = fits.open(filename)
    d = {}
    
