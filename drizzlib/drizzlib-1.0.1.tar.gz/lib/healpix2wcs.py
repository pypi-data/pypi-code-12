# Core imports
import os.path
import sys

# Numpy is your best friend when you have to handle numerical arrays of data
import numpy as np

# Healpy reads / writes to [HEALPix](http://healpix.sourceforge.net/) files
# Documentation for query_disc and query_polygon can be found in the source :
# https://github.com/healpy/healpy/blob/master/healpy/src/_query_disc.pyx
import healpy as hp

# Astropy offers some really nice FITS and coordinates conversion utils
# This package requires astropy version >= 1.0
from astropy import units as u
from astropy.coordinates import SkyCoord, Galactic
from astropy.io import fits
from astropy.wcs import WCS
from astropy.wcs.utils import wcs_to_celestial_frame

# From our C extension `src/optimized.c`, which stands for Polygon Clipping and
# helps us compute the area of intersection between WCS pixels and HEALPixels.
from optimized import intersection_area

# Our private utils
from utils import TAU, _wpix2hpix, _log


# PUBLIC FUNCTION #############################################################

# This @profile annotation is for `line_profiler`, see the bottom of this file.
# @profile
def healpix2wcs(
        healpix,
        field=1,
        header=None,
        header_hdu=0,
        output=None,
        crpix=None, cdelt=None,
        pixel_size=None,
        crval=None, ctype=None,
        image_size=None,
        equinox=2000.,
        use_bilinear_interpolation=False,
        ignore_blank=True,
        blank_value=-32768,
        clobber=False):
    """
    Extract a rectangular image in the WCS format from the provided HEALPix.
    The characteristics of the output WCS image are determined either by a
    provided header (which is a WCS FITS file path whose header cards we use),
    or directly using some parameters of this function.

    healpix: str
        The path to the input HEALPix file to read from.
    field: int
        The id of the HDU (Header Data Unit) to read in the HEALPix FITS file.
    header: file path, file object, or file-like object
        The (path to the) FITS file whose WCS header we want to read and use.
        If an opened file object, its mode must be one of the following :
        `rb`, `rb+`, or `ab+`.
    header_hdu: int
        The id of the HDU (Header Data Unit) to read in the header FITS file.
    output: str
        The path to the output FITS file that will be generated.
    crpix: float[2]
        Equivalent to the CRPIX FITS header card.
        A pair of floats, in the `Y,X` order.
        If you do not provide a header, you should provide this value.
        By default, will be
    cdelt: float[2]
        Equivalent to the CDELT FITS header card.
        A pair of floats, in the `Y,X` order.
        If you do not provide a header, you must provide this value, or the
        pixel_size parameter.
        This has a higher priority than the pixel_size parameter when both are
        provided.
    pixel_size: float
        The size of a square pixel in the output WCS.
        Will be used to create the cdelt if the latter is not specified.
        If you do not provide a header, you must provide this value, or the
        cdelt parameter.
        This has a lower priority than the pixel_size parameter when both are
        provided.
    crval: float[2]
        Equivalent to the CRVAL FITS header card.
        A pair of floats, in the `Y,X` order.
        If you do not provide a header, you must provide this value.
        As crpix is defaulted to the center of the image, this value should be
        the coordinates of the center of the output WCS image, for convenience.
    ctype: str[2]
        Equivalent to the CRVAL FITS header card.
        A pair of strings, in the `Y,X` order.
        If you do not provide a header, you must provide this value.
    image_size: int[2]
        The desired size in pixels of the output image.
        A pair of integers, in the `Y, X` order.
        If you do not provide a header, you must provide this value.
    equinox: float
        Equivalent to the EQUINOX FITS header card. Defaults to 2000.
        If you do not provide a header, you should provide this value.
    use_bilinear_interpolation: boolean
        Whether to use a simple bilinear interpolation instead of the more
        expensive surface-weighed mean.
    ignore_blank: boolean
        Whether or not to ignore the `BLANK` values in the input HEALPix.
        If no `BLANK` keyword is defined in the HEALPix FITS metadata, this has
        no effect.
    blank_value: int
        The BLANK value to use if it is not specified in the healpix header.
        Defaults to -32768.
    clobber: boolean
        Whether or not to overwrite (aka. clobber) the `output` file if it
        already exists.
    """

    if header is not None:
        # Read the settings from the WCS FITS file provided as header
        h = fits.getheader(header, header_hdu)
        w = WCS(h)
        # Extract the dimensions of the image from the header
        x_dim = h['NAXIS1']
        y_dim = h['NAXIS2']
        # Sanity check on the WCS headers.
        # You probably don't need this if you're not us, but it has little
        # to no effect on performance and it's very convenient for us.
        # We simply assert against the presence of both `CDELTn` and `CDn_n`.
        # print w.printwcs()
        if ('CDELT1' in h and 'CD1_1' in h) or (
                'CDELT1' in h and 'CD1_1' in h):
            raise ValueError(
                "Provided WCS headers have both CDELTn and CDn_n.")
    else:
        # User wants to provide the header cards directly as keyword arguments

        def _missing1(_property, _type='number'):
            raise ValueError("Provide either a FITS filepath in `header=`, "
                             "or a %ss in the property `%s=`."
                             % (_type, _property))

        def _missing2(_property, _type='number'):
            raise ValueError("Provide either a FITS filepath in `header=`, "
                             "or a pair of %ss in the property `%s=`."
                             % (_type, _property))

        if crval is None:
            _missing2('crval')
        if ctype is None:
            _missing2('ctype', 'string')
        if image_size is None:
            _missing2('image_size')
        if cdelt is None:
            if pixel_size is None:
                _missing1('pixel_size')
            cdelt = (-pixel_size, pixel_size)
        if crpix is None:
            crpix = (image_size[1] / 2., image_size[0] / 2.)

        # Create a new WCS object from scratch
        w = WCS(naxis=2)
        w.wcs.crpix = crpix
        w.wcs.cdelt = cdelt
        w.wcs.crval = crval
        w.wcs.ctype = ctype
        w.wcs.equinox = equinox

        x_dim = image_size[1]
        y_dim = image_size[0]

    # Sanitize
    x_dim = int(x_dim)
    y_dim = int(y_dim)

    # Debug
    _log("Using Python %s" % sys.version)

    # Make sure we can write to the output file
    if os.path.isfile(output) and not clobber:
        raise ValueError(
            "The output file '%s' already exists! "
            "Set clobber=True to overwrite." % output
        )

    # Read the input HEALPix FITS file.  /!\ Expensive operation !
    m, h = hp.read_map(healpix, h=True, hdu=field)

    # Define a private tool for accessing HEALPix header cards values
    # as the header h returned by the method above is only a list of tuples.
    def _get_hp_card(_name, _default=None):
        for (_card_name, _card_value) in h:
            if _name == _card_name:
                return _card_value
        return _default

    # Ignore BLANK values only if they are defined in the header
    blank = _get_hp_card('BLANK') or blank_value  # or -32768
    if blank is None:
        ignore_blank = False
    if ignore_blank:
        _log("Ignoring BLANK HEALPixels of value %.0f." % blank)
    else:
        _log("Not ignoring any blank pixels.")

    # Collect information about the HEALPix (it's faster to do this only once)
    nside = hp.get_nside(m)

    _log("%d HEALPixels in the whole map." % hp.get_map_size(m))

    # Guess the coordinates frame from the WCS header cards.
    # We highly rely on astropy here, so this may choke on illegal headers.
    frame = wcs_to_celestial_frame(w)
    _log("Coordinates frame is '%s'." % frame)

    # Instantiate the output data
    data = np.ndarray((y_dim, x_dim))

    ## FIRST PASS
    # Collect the HPX coordinates of the center and corners of each WCS pixel.
    # We use the corners to efficiently select the healpixels to drizzle for
    # each WCS pixel, in the third pass.
    x_center = np.ndarray((y_dim, x_dim))
    y_center = np.ndarray((y_dim, x_dim))
    x_corner = np.ndarray((4, y_dim, x_dim))
    y_corner = np.ndarray((4, y_dim, x_dim))

    # WARNING: optimal padding (10% right now) has NOT been determined.
    #          if too low, results are incorrect
    #          if too high, performance suffers
    #          the current value of 10% is a "gut value".
    pad = 0.5 * 1.05  # bigger, to compensate the non-affine transformation

    for x in range(x_dim):
        for y in range(y_dim):
            x_center[y, x] = x
            y_center[y, x] = y
            x_corner[:, y, x] = np.array([x - pad, x + pad, x + pad, x - pad])
            y_corner[:, y, x] = np.array([y + pad, y + pad, y - pad, y - pad])

    # Transforming coordinates to the Galactic referential is faster with
    # one SkyCoord object than with many, hence this first pass, which enables
    # us to vectorize the transformation.
    [lat_centers, lng_centers] = _wpix2hpix([x_center, y_center], w, frame)
    [lat_corners, lng_corners] = _wpix2hpix([x_corner, y_corner], w, frame)

    ## NEXT -- Two very different methods are available
    if use_bilinear_interpolation:
        # SECOND PASS : bilinear interpolation is fast and easy, but it will
        # yield incorrect results in some edge cases.
        # With that method we only have two passes, and we're done.
        for x in range(int(x_dim)):
            for y in range(int(y_dim)):
                # Coordinates in HEALPix space of the center of this pixel
                # Those are Quantity objects, so we pick their `value`
                theta = lat_centers[y, x].value
                phi = lng_centers[y, x].value

                # Healpy's bilinear interpolation
                v_interp = hp.get_interp_val(m, theta, phi)

                data[y, x] = v_interp

    else:
        # SECOND PASS : We use a intersection-surface weighed mean.
        # As converting our healpix polygons into pixel coords
        # is really expensive (like 84% of total time), we vectorize it.
        # This means selecting beforehand the HEALPixels intersecting with our
        # WCS image, and we do that by creating a polygon around our WCS image,
        # and using that polygon with `healpy`'s `query_polygon` method.
        # This makes the code harder to understand, but also much faster.

        # Memoization holder for the cartesian vertices of healpixs on
        # the flat plane of the projection.
        hpix_polys = [None] * hp.get_map_size(m)
        # The above list initialization is much, much faster than :
        # hpix_polys = [None for _ in range(hp.get_map_size(m))]

        # We optimize by selecting beforehand the healpixels that intersect
        # with our WCS image, using `healpy.query_polygon`.
        # That optimization is disabled for wholesky plate carree projections.
        if 'CAR' in w.wcs.ctype[0] or 'CAR' in w.wcs.ctype[1]:
            # Disable the optimization by selecting all healpixels
            wrap_healpixs = range(hp.get_map_size(m))
        else:
            # As the referential change from HEALPix to WCS is non-affine, a
            # simple rectangle of the size of the WCS image is not sufficient,
            # as it will miss some HEALPixels.
            # So we (arbitrarily!) pad it to make it a little big bigger.
            # The optimal padding can probably be mathematically computed,
            # but I have no idea as to how.
            # WARNING: THIS WILL CRASH AND BURN WITH WHOLE SKY CAR PROJECTIONS
            pad = 0.05 * (x_dim + y_dim) / 2.
            wrap_poly_vertices = np.transpose(np.array([
                [-0.5 - pad, -0.5 - pad],
                [-0.5 - pad, y_dim - 0.5 + pad],
                [x_dim - 0.5 + pad, y_dim - 0.5 + pad],
                [x_dim - 0.5 + pad, -0.5 - pad],
            ]))
            wrap_poly_hp = _wpix2hpix(wrap_poly_vertices, w, frame)
            wrap_poly_hp = hp.ang2vec([v.value for v in wrap_poly_hp[0]],
                                      [v.value for v in wrap_poly_hp[1]])
            wrap_healpixs = hp.query_polygon(nside, wrap_poly_hp,
                                             inclusive=True)

        _log("%d HEALPixels in the WCS wrapper polygon." % len(wrap_healpixs))

        # Collect the vector coordinates of the corners in the hp ref.
        # [ [x1, x2, ..., xn], [y1, y2, ..., yn], [z1, z2, ..., zn] ]
        corners_hp_vec = np.ndarray((3, len(wrap_healpixs) * 4))
        for i in range(len(wrap_healpixs)):
            # [ [x1, x2, x3, x4], [y1, y2, y3, y4], [z1, z2, z3, z4] ]
            corners = hp.boundaries(nside, wrap_healpixs[i])
            j = i * 4
            corners_hp_vec[0][j:j + 4] = corners[0]
            corners_hp_vec[1][j:j + 4] = corners[1]
            corners_hp_vec[2][j:j + 4] = corners[2]

        # Convert the corners into (theta, phi) (still in hp ref.)
        # [ [t1, t2, ..., tn], [p1, p2, ..., pn] ]
        corners_hp_ang = hp.vec2ang(np.transpose(corners_hp_vec))

        # Build the (expensive!) SkyCoord object with all our coords
        sky_b = -1 * (corners_hp_ang[0] * 360. / TAU - 90.)
        sky_l = corners_hp_ang[1] * 360. / TAU
        sky = SkyCoord(b=sky_b, l=sky_l, unit=u.degree, frame=Galactic)

        # Convert the corners to the WCS pixel space
        cors_gal_x, cors_gal_y = sky.to_pixel(w)

        # Store in memory the HEALPix polygons geometry in WCS pixel space
        for i in range(len(wrap_healpixs)):
            j = i * 4
            # Finally, we make a list of (x, y) vertices in pixel referential,
            # which we index per healpixel id for later usage in the loop.
            hpix_poly = np.transpose([cors_gal_x[j:j+4], cors_gal_y[j:j+4]])
            hpix_polys[wrap_healpixs[i]] = hpix_poly

        # This plotting helps debugging the above optimization
        # wcs_pix_polys = []
        # for x in range(int(x_dim)):
        #     for y in range(int(y_dim)):
        #         wpix_poly = np.array([
        #             [x - 0.5, y + 0.5],
        #             [x - 0.5, y - 0.5],
        #             [x + 0.5, y - 0.5],
        #             [x + 0.5, y + 0.5],
        #         ])
        #         wcs_pix_polys.append(wpix_poly)
        # _dbg_plot_poly(hpix_polys, wcs_pix_polys)
        ######################################################

        # THIRD PASS : rasterize healpixels on the (finite) wcs grid,
        # picking a mean pondered by the intersection area.
        # For each WCS pixel in the WCS image...
        for x in range(x_dim):
            for y in range(y_dim):

                # Vertices of the WCS pixel in WCS pixel space
                wpix_poly = np.array([
                    [x - 0.5, y - 0.5],
                    [x - 0.5, y + 0.5],
                    [x + 0.5, y + 0.5],
                    [x + 0.5, y - 0.5],
                ])

                # This gives results that are different from IDL
                # todo: why isn't it like this ? I don't get it.
                # wpix_poly = np.array([
                #     [x,     y],
                #     [x,     y + 1],
                #     [x + 1, y + 1],
                #     [x + 1, y]
                # ])

                # Tallies to compute the weighted arithmetic mean
                total = 0
                value = 0

                # Find all the HEALPixels that intersect with a polygon
                # slightly bigger than the pixel, whose vertices were computed
                # in the first pass.
                # Those are Quantity objects, so we pick their `value`.
                wrap_pix = hp.ang2vec(lat_corners[:, y, x].value,
                                      lng_corners[:, y, x].value)
                hpix_ids = hp.query_polygon(nside, wrap_pix, inclusive=True)

                # For each healpixel, we're going to figure out its
                # contribution to the WCS pixel (how much they intersect)
                for hpix_id in hpix_ids:

                    # Healpy might return -1 when not found, ignore those.
                    if hpix_id == -1:
                        continue

                    hpix_value = m[hpix_id]

                    # Ignore BLANK values if configuration allows.
                    if ignore_blank and hpix_value == blank:
                        continue

                    hpix_poly = hpix_polys[hpix_id]

                    if hpix_poly is None:
                        # Even though we try to precompute the polygons in one
                        # fell swoop to avoid the expensive instanciation of a
                        # SkyCoord object, some pixels might fall through the
                        # cracks and need to be converted on the fly.
                        # It's okay if this happens a couple of times,
                        # but if it happens too often, we lose in performance.
                        _log("\nWarning: healpixel %s escaped optimization."
                             % hpix_id)

                        corners = hp.boundaries(nside, hpix_id)
                        theta_phi = hp.vec2ang(np.transpose(corners))

                        sky_b = -1 * (theta_phi[0] * 360. / TAU - 90.)
                        sky_l = theta_phi[1] * 360. / TAU
                        sky = SkyCoord(b=sky_b, l=sky_l, unit=u.degree,
                                       frame=Galactic)

                        # Finally, make a list of (x, y) in pixel referential
                        hpix_poly = np.transpose(sky.to_pixel(w))
                        # ...which we memoize
                        hpix_polys[hpix_id] = hpix_poly

                    # Optimized C implementation of Sutherland-Hodgeman
                    # `intersection_area` is defined in `src/optimized.c`.
                    # The intersection is computed in pixel space.
                    shared_area = intersection_area(hpix_poly, 4,
                                                    wpix_poly, 4)

                    total += shared_area
                    value += shared_area * hpix_value

                if total != 0:
                    v_drizzle = value / total
                else:
                    v_drizzle = value
                    _log("Warning: Sum of weights at (%d, %d) is 0." % (x, y))

                data[y, x] = v_drizzle

        _log("\n")

    if output is not None:
        fits.writeto(output, data, header=w.to_header(), clobber=clobber)

    return data


### FOR THE PROFILER ##########################################################

# $ pip install line_profiler
# add @profile before the function you want to profile, and then run :
# $ kernprof -v -l drizzlib.py
# if __name__ == "__main__":
#     try:
#         healpix2wcs(
#             'tests/healpix/HFI_SkyMap_857_2048_R1.10_nominal_ZodiCorrected.fits',
#             header='tests/wcs/iris_100_2000_21jun06_bpix.fits',
#             output='tests/wcs/test.fits',
#             clobber=True
#         )
#     except KeyboardInterrupt:
#         pass