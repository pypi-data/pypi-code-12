
def SRS_from_WKT(s):
    """ Return Proj.4 string, semimajor axis, and flattening """
    sr = osgeo.osr.SpatialReference()
    sr.ImportFromWkt(s)
    return sr

def proj4_isgeodetic(s):
    return ("lonlat" in s) or ("longlat" in s) or \
            ("latlon" in s) or ("latlong" in s)

