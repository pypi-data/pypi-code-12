# Core imports
from sys import getsizeof
from itertools import chain
from collections import deque

# Numpy is your best friend when you have to handle numerical arrays of data.
import numpy as np

# Healpy reads / writes to [HEALPix](http://healpix.sourceforge.net/) files.
import healpy as hp

# Astropy offers some really nice FITS and conversion utils
# Our code requires astropy version >= 1.0
from astropy import units as u
from astropy.coordinates import SkyCoord, Galactic

# The TRUE Circle Constant (http://tauday.com/tau-manifesto).
TAU = np.pi * 2.


## SCIENCE ####################################################################


def _galactic2healpix(sky):
    """
    Acessing SkyCoord's properties is expensive, so we do it only once, and we
    also convert the coordinates to a spherical representation suitable
    for healpy. Also, note that sky's properties are Quantities, with Units,
    and so are the returned values of this function.
    See astropy.units for more information about Quantities and Units.
    """
    lats = (90. * u.degree - sky.b) * TAU / 360.  # 90 is for colatitude
    lngs = sky.l * TAU / 360.

    return [lats, lngs]


def _wpix2hpix(coords, wcs, frame):
    """
    From WCS pixel space (x/y) to HEALPix space (lat/lon).

    coords: ndarray
        Of shape (2, ...)

    Returns two Quantities, each of shape (...) matching the input `coords`.
    """
    # The order of the axes for the result is determined by the CTYPEia
    # keywords in the FITS header, therefore it may not always be of the
    # form (ra, dec). The lat, lng, lattyp and lngtyp members can be
    # used to determine the order of the axes.
    [lats, lngs] = wcs.all_pix2world(coords[0], coords[1], 0)
    sky = SkyCoord(lats, lngs, unit=u.degree, frame=frame)

    return _galactic2healpix(sky.transform_to(Galactic))


def _project_hpix_polys_to_wcs(nside, wcs, is_origin_center=False,
                               x_dim=None, y_dim=None):
    """
    Return a list of lists of 8*n (x, y) tuples, which are the coordinates of
    the vertices of the healpixels when projected into the `wcs` plane.

    For each healpixel there may be two polygons, in case the WCS is a
    whole sky CAR and the healpix is on the edge (two polygons, one on the
    right, one on the left).
    Most of the healpixels in most of the cases will only have one polygon.

    The count of polygons per healpixel is returned as second value.

    This function only supports nsides <= 1024 (the RAM explodes after that).

    [
        # healpixel #1 vertices in X,Y format, in WCS pixel space
        [
            (1, 5),
            (1, 7),
            (2, 7),
            (2, 5),  # won't be as square as that in practice
        ],
        # healpixek #2...
    ]
    """
    assert x_dim is not None and y_dim is not None, "Provide x_dim= and y_dim="

    x_off = 0
    y_off = 0
    if is_origin_center:
        x_off = x_dim / 2.
        y_off = y_dim / 2.

    npix = hp.nside2npix(nside)
    # Ids of the healpixels to process (may be parameterized later)
    # todo: will probably need to refactor this when chunking for RAM usage
    healpixs = np.arange(npix)
    # Holder for the cartesian vertices of healpixs on the projection plane
    # The second axis is 8 because if there are two 4-sided polygons they
    # will be packed in the 8 values. Otherwise, half the values are unused.
    hpix_polys = np.zeros((npix, 8, 2))
    # The tally is the count of polygons (1 or 2) per healpixel
    hpix_tally = [1] * npix
    # Collect the vector coordinates of the corners in the healpix referential
    # [ [x1, x2, ..., xn], [y1, y2, ..., yn], [z1, z2, ..., zn] ]
    corners_hp_vec = np.ndarray((3, len(healpixs) * 4))
    for i, healpix in enumerate(healpixs):
        # [ [x1, x2, x3, x4], [y1, y2, y3, y4], [z1, z2, z3, z4] ]
        corners = hp.boundaries(nside, healpix)
        j = i*4
        assert corners is not None, \
            "healpy.boundaries(%d, %d) returned None, try upgrading healpy: " \
            "pip install healpy --upgrade" % (nside, healpix)
        corners_hp_vec[0][j:j+4] = corners[0]
        corners_hp_vec[1][j:j+4] = corners[1]
        corners_hp_vec[2][j:j+4] = corners[2]

    # Convert the corners into (theta, phi) (still in hp ref.)
    # [ [t1, t2, ..., tn], [p1, p2, ..., pn] ]
    corners_hp_ang = hp.vec2ang(np.transpose(corners_hp_vec))

    # Prepare the lat/lon in degrees, from radians, handling colatitude too.
    sky_b = -1 * (corners_hp_ang[0] * 360. / TAU - 90.)  # lat
    sky_l = corners_hp_ang[1] * 360. / TAU               # lon

    # fixme : explain why we need to rotate like this here (i have no idea)
    # Maybe it's business with colatitude ? Maybe a header keyword we ignore ?
    from healpy import rotator
    rh2w_angles = [0, -90, 180]
    rh2w = rotator.Rotator(rot=rh2w_angles)
    rw2h = rotator.Rotator(rot=rh2w_angles, inv=True)
    sky_l, sky_b = rh2w(sky_l, sky_b, lonlat=True)
    ###################################################

    # Build the (expensive!) SkyCoord object with all our coords
    sky = SkyCoord(b=sky_b, l=sky_l, unit=u.degree, frame=Galactic)

    # Convert the corners to the WCS pixel space
    # Note: If WCS projection is CAR we can have negative values for x and y.
    cors_gal_x, cors_gal_y = sky.to_pixel(wcs)

    # Debugging
    # pixels_to_examine = [  # x, y order
    #     (0, 0),
    #     (-720, -360),
    #     (-720, +360),
    #     (+720, +360),
    #     (+720, -360),
    #     (-719.5, -359.5),
    #     (-719.5, +359.5),
    #     (+719.5, +359.5),
    #     (+719.5, -359.5),
    # ]
    #
    # for _x, _y in pixels_to_examine:
    #     tmp = SkyCoord.from_pixel(_x, _y, wcs)
    #     print "Pixel (%.1f, %.1f) coordinates :" % (_x, _y), tmp
    #     print "  After rotation", rw2h(tmp.l.value, tmp.b.value, lonlat=True)

    # Unpack & store in memory the HEALPix polygons geometry in WCS pixel space
    for i, healpix in enumerate(healpixs):
        j = i*4
        # Finally, we make a list of (x, y) vertices in pixel referential,
        # which we index per healpixel id for later usage in the loop.
        hpix_polys[healpix][0:4] = np.transpose([cors_gal_x[j:j+4], cors_gal_y[j:j+4]])

    is_full_sky = _is_full_sky_wcs(wcs, x_dim, y_dim)
    if is_full_sky:
        # Some WCS maps are seamless at the west and east edges,
        # so we duplicate the healpolygons that cross the west and east edges.
        # We're going to copy and translate some vertices, to simulate
        # a projection on a semi-seamless plane.
        # But sometimes our input wcs images are LARGER than the sky
        sky_x_dim = (360 * u.degree) / (wcs.wcs.cdelt[1] * u.Unit(wcs.wcs.cunit[1]))
        sky_x_dim = sky_x_dim.value

        for i, healpix in enumerate(healpixs):
            j = i*4

            # If any of the diagonals of the polygon is too big
            # This is *really* hackish ; to replace this, the idea is to
            # pre-select the healpixels on the edges using healpix queries.
            if (((cors_gal_x[j+0]-cors_gal_x[j+2])**2 + (cors_gal_y[j+0]-cors_gal_y[j+2])**2) ** .5 > 0.5 * (x_dim*y_dim)**.5).any() or\
               (((cors_gal_x[j+1]-cors_gal_x[j+3])**2 + (cors_gal_y[j+1]-cors_gal_y[j+3])**2) ** .5 > 0.5 * (x_dim*y_dim)**.5).any():

                # Polygon on the left
                left_x = cors_gal_x[j:j+4].copy()
                iotr_x = left_x + x_off > x_dim / 2.  # Indices On The Right
                left_x[iotr_x] = left_x[iotr_x] - sky_x_dim
                left = np.transpose([left_x, cors_gal_y[j:j+4]])

                # Polygon on the right
                right_x = cors_gal_x[j:j+4].copy()
                iotl_x = right_x + x_off < x_dim / 2.  # Indices On The Left
                right_x[iotl_x] = right_x[iotl_x] + sky_x_dim
                right = np.transpose([right_x, cors_gal_y[j:j+4]])

                hpix_polys[healpix] = np.vstack((right, left))
                hpix_tally[healpix] = 2

    return hpix_polys, np.array(hpix_tally)


def _is_full_sky_wcs(wcs, x_dim, y_dim):
    """
    This is to detect "special cases" : wholesky, seamless, equirectangular
    projection (CAR).
    We need to duplicate the seam edge healpixels on each edge when we project
    their geometry on the WCS plane if it is full sky, because its vertical
    edges are seamless.
    This is the case notably with the plate carree projection CAR.
    Note: we may have input WCS images a bit _larger_ than the sky.
    """
    from astropy.units import Unit
    from astropy.units import degree
    is_car = wcs.wcs.ctype[0].endswith('CAR')
    y_size = abs(wcs.wcs.cdelt[0] * Unit(wcs.wcs.cunit[0])) * y_dim
    x_size = abs(wcs.wcs.cdelt[1] * Unit(wcs.wcs.cunit[1])) * x_dim

    return is_car and y_size >= 180 * degree and x_size >= 360 * degree


## SYSTEM #####################################################################


def _log(something):
    """
    Uninspired logging utility. Overwrite at will.
    Use the `logging` module instead of print ?
    """
    print("%s" % something)


def _human_file_size(filename):
    """
    Reads the disk size of the file described by its `filename`,
    as a string suitable to human eyes.
    (a blind person actually passed by me as I wrote that on a train.)
    Can possibly be vastly improved, only works with Mio right now.
    """
    from os.path import getsize
    octets = getsize(filename)
    mio = octets / (2.**20)
    return "%.1f Mio" % mio


def _mem(o):
    """
    Return the memory footprint of a variable, as a humanized string.
    """
    from pympler.asizeof import asizeof
    return _sizeof_fmt(asizeof(o))


def _total_sizeof(o):
    """
    Return the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    """
    dict_handler = lambda d: chain.from_iterable(d.items())
    all_handlers = {
        tuple: iter,
        list: iter,
        deque: iter,
        dict: dict_handler,
        set: iter,
        frozenset: iter,
    }
    seen = set()  # track which object id's have already been seen
    default_size = getsizeof(0)  # estimate sizeof object without __sizeof__

    def sizeof(_o):
        if id(_o) in seen:  # do not double count the same object
            return 0
        seen.add(id(_o))

        if isinstance(_o, np.ndarray):
            s = _o.nbytes
        else:
            s = getsizeof(_o, default_size)

        for typ, handler in all_handlers.items():
            if isinstance(_o, typ):
                s += sum(map(sizeof, handler(_o)))
                break
        return s

    return sizeof(o)


def _sizeof_fmt(num, suffix='o'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0

    return "%.1f%s%s" % (num, 'Yi', suffix)


def dbg_plot_poly(healpolygons, wcspolygons):
    """
    This debug tool can be used to plot the healpix polygons, and the wcs grid
    in surimposition.
    This is more useful than initially thought.
    It should be improved and outsourced.

    healpolygons:
        List of lists of N>2 (x,y) tuples.
    wcspolygons:
        List of lists of N>2 (x,y) tuples.
    """
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches

    fig = plt.figure()
    ax = fig.add_subplot(111)

    xmin = 0
    xmax = 1
    ymin = 0
    ymax = 1

    for polygon in healpolygons:

        if polygon is None:
            continue

        verts = list(polygon)
        length = len(verts)

        xy = np.transpose(verts)
        xmin = min(xmin, np.min(xy[0]))
        xmax = max(xmax, np.max(xy[0]))
        ymin = min(ymin, np.min(xy[1]))
        ymax = max(ymax, np.max(xy[1]))

        verts.append((0., 0.))

        codes = [Path.MOVETO]
        for j in range(length-1):
            codes.append(Path.LINETO)
        codes.append(Path.CLOSEPOLY)

        path = Path(verts, codes)

        patch = patches.PathPatch(path, facecolor='orange', lw=1)
        ax.add_patch(patch)

    for polygon in wcspolygons:

        verts = list(polygon)
        length = len(verts)

        xy = np.transpose(verts)
        xmin = min(xmin, np.min(xy[0]))
        xmax = max(xmax, np.max(xy[0]))
        ymin = min(ymin, np.min(xy[1]))
        ymax = max(ymax, np.max(xy[1]))

        verts.append((0., 0.))

        codes = [Path.MOVETO]
        for j in range(length-1):
            codes.append(Path.LINETO)
        codes.append(Path.CLOSEPOLY)

        path = Path(verts, codes)

        patch = patches.PathPatch(path, alpha=0.3, facecolor='blue', lw=1)
        ax.add_patch(patch)
    xpad = (xmax - xmin) * 0.05
    ypad = (ymax - ymin) * 0.05
    ax.set_xlim(xmin - xpad, xmax + xpad)
    ax.set_ylim(ymin - ypad, ymax + ypad)

    plt.show()