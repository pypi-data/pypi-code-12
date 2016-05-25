

class Map_Base(object):
    """ Abstract representation of a 2D or 3D counts map."""

    def __init__(self, counts):
        self._counts = counts

    @property
    def counts(self):
        return self._counts


class Map(Map_Base):
    """ Representation of a 2D or 3D counts map using WCS. """

    def __init__(self, counts, wcs):
        """
        Parameters
        ----------
        counts : `~numpy.ndarray`
          Counts array.
        """
        Map_Base.__init__(self, counts)
        self._wcs = wcs

    @property
    def wcs(self):
        return self._wcs

    @staticmethod
    def create_from_hdu(hdu, wcs):
        return Map(hdu.data.T, wcs)

    @staticmethod
    def create_from_fits(fitsfile, **kwargs):
        hdu = kwargs.get('hdu', 0)

        hdulist = pyfits.open(fitsfile)
        header = hdulist[hdu].header
        data = hdulist[hdu].data
        header = pyfits.Header.fromstring(header.tostring())
        wcs = pywcs.WCS(header)
        return Map(data, wcs)
