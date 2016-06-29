from astropy.coordinates import match_coordinates_sky, SkyCoord
from astropy import units as u
from astropy import table
from astropy import io
from astropy import wcs
import os
import numpy as np

import utilities


def symmetric_match(table_1, table_2, ra_col_1="ra", ra_col_2="ra",
          dec_col_1="dec", dec_col_2="dec", max_sep=3.0):
    """
    Matches objects from two astropy tables by ra/dec.

    This function does symmetric matching. This measns that to be defined as
    a match, both objects must be each other's closest match. Their separation
    must also be less than the `max_sep` parameter.

    :param table_1: First astopy table object containing objects with ra/dec
                    information.
    :param table_2: First astopy table object containing objects with ra/dec
                    information.
    :param ra_col_1: Name of the ra column in table_1. Defaults to "ra".
    :param ra_col_2: Name of the ra column in table_2. Defaults to "ra".
    :param dec_col_1: Name of the dec column in table_1. Defaults to "dec".
    :param dec_col_2: Name of the dec column in table_2. Defaults to "dec".
    :param max_sep: Maximum separation (in arcseconds) allowed for two objects
                    to be considered a match.
    :return: Astropy table object containing the matches between the two
             input table objects. All columns from both catalogs will be
             included, as well as a separate separation column.
    """



    coords_1 = SkyCoord(table_1[ra_col_1], table_1[dec_col_1], unit=u.degree)
    coords_2 = SkyCoord(table_2[ra_col_2], table_2[dec_col_2], unit=u.degree)

    # find matches for objects in table 1 in table 2
    match_idx_12, sep_12, dist_12 = match_coordinates_sky(coords_1, coords_2)
    # and find matches for objects in table 2 in table 1
    match_idx_21, sep_21, dist_21 = match_coordinates_sky(coords_2, coords_1)

    # now check that the matching is symmetric
    symmetric_12 = []
    for idx_1, match_idx in enumerate(match_idx_12):
        if idx_1 == match_idx_21[match_idx] and sep_12[idx_1].arcsec < max_sep:
            symmetric_12.append((idx_1, match_idx, sep_12[idx_1].arcsec))

    idx_1, idx_2, sep = zip(*symmetric_12)

    idx_1 = list(idx_1)
    idx_2 = list(idx_2)
    sep = list(sep)

    # now turn into astropy table
    matches = table_1[idx_1]
    # get only the ones from table_2 that have matches
    matches_2 = table_2[idx_2]

    for col in matches_2.colnames:
        if col in matches.colnames:
            matches_2.rename_column(col, col + "_2")
            matches.add_column(matches_2[col + "_2"])
        else:
            matches.add_column(matches_2[col])

    matches.add_column(table.Column(data=sep * u.arcsec, name="sep [arcsec]"))

    return matches





def symmetric_match_both(table_1, table_2, ra_col_1="ra", ra_col_2="ra",
          dec_col_1="dec", dec_col_2="dec", max_sep=3.0):
    """
    Matches objects from two astropy tables by ra/dec, including all objects.

    This function does symmetric matching. This measns that to be defined as
    a match, both objects must be each other's closest match. Their separation
    must also be less than the `max_sep` parameter.

    Each object from both tables is included, even if there are no matches
    for that object. The empty space will be filled with the appropriate 
    empty data.

    :param table_1: First astopy table object containing objects with ra/dec
                    information.
    :param table_2: First astopy table object containing objects with ra/dec
                    information.
    :param ra_col_1: Name of the ra column in table_1. Defaults to "ra".
    :param ra_col_2: Name of the ra column in table_2. Defaults to "ra".
    :param dec_col_1: Name of the dec column in table_1. Defaults to "dec".
    :param dec_col_2: Name of the dec column in table_2. Defaults to "dec".
    :param max_sep: Maximum separation (in arcseconds) allowed for two objects
                    to be considered a match.
    :return: Astropy table object containing the matches between the two
             input table objects. All columns from both catalogs will be
             included, as well as a separate separation column.
    """

    coords_1 = SkyCoord(table_1[ra_col_1], table_1[dec_col_1], unit=u.degree)
    coords_2 = SkyCoord(table_2[ra_col_2], table_2[dec_col_2], unit=u.degree)

    # find matches for objects in table 1 in table 2
    match_idx_12, sep_12, dist_12 = match_coordinates_sky(coords_1, coords_2)
    # and find matches for objects in table 2 in table 1
    match_idx_21, sep_21, dist_21 = match_coordinates_sky(coords_2, coords_1)

    # now check that the matching is symmetric
    symmetric_12 = []
    for idx_1, match_idx in enumerate(match_idx_12):
        if idx_1 == match_idx_21[match_idx] and sep_12[idx_1].arcsec < max_sep:
            symmetric_12.append((idx_1, match_idx, sep_12[idx_1].arcsec))

    idx_1, idx_2, sep = zip(*symmetric_12)

    idx_1 = list(idx_1)
    idx_2 = list(idx_2)
    sep = list(sep)

    # now turn into astropy table
    matches = table_1[idx_1]
    # get only the ones from table_2 that have matches
    matches_2 = table_2[idx_2]

    for col in matches_2.colnames:
        if col in matches.colnames:
            matches_2.rename_column(col, col + "_2")
            matches.add_column(matches_2[col + "_2"])
        else:
            matches.add_column(matches_2[col])
            
    matches.add_column(table.Column(data=sep * u.arcsec, name="sep [arcsec]"))
            
    # This adds all the matches. We need to add all the non-matches
    non_matches_1 = table_1.copy()
    non_matches_2 = table_2.copy()
    non_matches_1.remove_rows(idx_1)
    non_matches_2.remove_rows(idx_2)

    for row in non_matches_1:
        new_row = [item for item in row]
        for colname in matches.colnames[len(new_row):]:
            new_row.append(utilities.empty_data(matches[colname].dtype))
        matches.add_row(new_row)
    
    for row in non_matches_2:
        new_row = []
        for colname in matches.colnames[:len(non_matches_1.colnames)]:
            new_row.append(utilities.empty_data(matches[colname].dtype))
        for item in row:
            new_row.append(item)
            
        # add extra spot for separation
        new_row.append(np.nan)
            
        matches.add_row(new_row)


    return matches

def match_one(table_1, table_2, ra_col_1="ra", ra_col_2="ra",
          dec_col_1="dec", dec_col_2="dec", max_sep=3.0,
          include_all_from_1=False):
    """
    Matches objects from two astropy tables by ra/dec. All objects from the 
    first will be matched to one in the second. 


    :param table_1: First astopy table object containing objects with ra/dec
                    information.
    :param table_2: First astopy table object containing objects with ra/dec
                    information.
    :param ra_col_1: Name of the ra column in table_1. Defaults to "ra".
    :param ra_col_2: Name of the ra column in table_2. Defaults to "ra".
    :param dec_col_1: Name of the dec column in table_1. Defaults to "dec".
    :param dec_col_2: Name of the dec column in table_2. Defaults to "dec".
    :param max_sep: Maximum separation (in arcseconds) allowed for two objects
                    to be considered a match.
    :param include_all_from_1: Whether or not to include all rows from table 1,
                               not just those that have matches.
    :return: Astropy table object containing the matches between the two
             input table objects. All columns from both catalogs will be
             included, as well as a separate separation column.
    """

    coords_1 = SkyCoord(table_1[ra_col_1], table_1[dec_col_1], unit=u.degree)
    coords_2 = SkyCoord(table_2[ra_col_2], table_2[dec_col_2], unit=u.degree)
    
    

    # find matches for objects in table 1 in table 2
    match_idx_12, sep_12, dist_12 = match_coordinates_sky(coords_1, coords_2)
    # and find matches for objects in table 2 in table 1
    match_idx_21, sep_21, dist_21 = match_coordinates_sky(coords_2, coords_1)
    
    # get the matches that are close enough, and those separations
    match_idx = match_idx_12[np.where(sep_12 < max_sep * u.arcsec)]
    sep = sep_12[np.where(sep_12 < max_sep * u.arcsec)]

    # now trim the table into ones that have a close match.
    matches = table_1[np.where(sep_12 < max_sep * u.arcsec)]
    # get only the ones from table_2 that have matches
    matches_2 = table_2[match_idx]

    for col in matches_2.colnames:
        if col in matches.colnames:
            matches_2.rename_column(col, col + "_2")
            matches.add_column(matches_2[col + "_2"])
        else:
            matches.add_column(matches_2[col])
            
    matches.add_column(table.Column(data=sep.arcsec, name="sep [arcsec]"))

    if include_all_from_1:
        # We added all the matches, we need to include all the non-matches.
        non_matches_1 = table_1[np.where(sep_12 > max_sep * u.arcsec)]

        # add all to the new_table
        for row in non_matches_1:
            new_row = [item for item in row]
            # we have to fill the rest with empty data, since nothing exists.
            # get the leftover columns
            for colname in matches.colnames[len(new_row):]:
                # then add empty data of the appropriate type
                new_row.append(utilities.empty_data(matches[colname].dtype))
            # we have a full row, so we can add it.
            matches.add_row(new_row)

    return matches


def pretty_write(table, out_file, clobber=False):
    """
    Writes an astropy table in a nice format.

    :param table: Astropy table object to write to file.
    :type table: astropy.table.Table
    :param out_file: Place to write the resulting ascii file. 
    :type out_file: str
    :param clobber: Whether or not to overwrite an existing file, if it exists.
                    If this is false, the function will exit with an error if
                    a file already exists here. If clobber is True, it will
                    overwrite the file there.
    :type clobber: bool

    """
    # first check if a file exists there, and raise an error if it does.
    if not clobber:
        if utilities.check_if_file(out_file):
            raise IOError("File already exists. "
                          "Set `clobber=True` if you want to overwrite. ")
    # will continue if no error is raised.
    
    with open(out_file, "w") as output:
        # set an empty string that defines how the formatting will work, that
        # we will add to as we go
        formatting = ""
        first = True # have to keep track of the first one

        # then use the column names and data within to determine the width each
        # column will need when written to a file, and put that info in the
        # formatter variable
        for col in table.colnames:
            # find the maximum length of either the column name of the
            # data in that column. For data, get the length of the string
            # representation of the object, since that's what will be
            # written to the file

            max_data_len = max([len(str(item)) for item in table[col]])
            max_len = max(max_data_len, len(col))
            max_len += 5  # add 5 to make it spread out nicer
            
            # if it's the first one, add extra for the comment
            if first:
                max_len += 2
                first = False
            
            # use this info to add the next part of the formatter
            # the double braces are so we can get actual braces, then the 
            # length goes after the "<"
            formatting += "{{:<{}}}".format(max_len)

        # we are now done with the formatting string, so add a newline
        formatting += "\n"
        
        # Now write the header column
        colnames = table.colnames
        # add a comment to the first one
        colnames[0] = "# " + colnames[0]
        output.write(formatting.format(*colnames))
        
        # then write all the data
        for line in table:
            output.write(formatting.format(*line))
        

def wcs_to_xy(ra, dec, image_path):
    """
    Turn lists of RA and Dec into pixel values for a given image.

    This is just a wrapper for the wcs tools in astropy, and it returns the
    same thing as the Astropy `wcs.all_world2pix()` function.

    The best way to call this function is to do:
    `x, y = wcs_to_xy(ra, dec, image_path)`

    Also note the `table_wcs_to_xy()` function, which is a wrapper for this 
    function when you have an astropy table containing your RA and Dec.
    
    :param ra: List of RA values.
    :type ra: list of floats
    :param dec: List of Dec values.
    :type dec: list of floats
    :param image_path: File path to the FITS image that will used to calculate 
                       the pixel values. 
    :type image_path: str
    :return: Lists of the x and y pixel values of the objects. 
    :rtype: tuple of lists of floats

    """
    image_wcs = wcs.WCS(image_path)
    return image_wcs.all_world2pix(ra, dec, 1)

def xy_to_wcs(x, y, image_path):
    """
    Turn lists of x and y pixel locations into RA and Dec for a given image.

    This is just a wrapper for the wcs tools in astropy, and it returns the
    same thing as the Astropy `wcs.all_pix2world()` function.

    The best way to call this function is to do:
    `ra, dec = xy_to_wcs(x, y, image_path)`

    Also note the `table_x_to_wcs()` function, which is a wrapper for this 
    function when you have an astropy table containing your x and y values.
    
    :param x: List of x pixel locations.
    :type x: list of floats
    :param y: List of y pixel locations.
    :type y: list of floats
    :param image_path: File path to the FITS image that will used to calculate 
                       the WCS coordinates. 
    :type image_path: str
    :return: Lists of the ra and dec of the objects. 
    :rtype: tuple of lists of floats
    """
    image_wcs = wcs.WCS(image_path)
    return image_wcs.all_pix2world(x, y, 1)

def table_wcs_to_xy(catalog, image_path, ra_col="ra", dec_col="dec",
                    x_col="x", y_col="y"):
    """
    Adds x and y pixel location columns to a table containig RA/Dec info.

    This function takes an astropy table with columns containing the RA and Dec
    of the objects, and adds columns containing the x and y pixel values of
    these objects in a given image. 

    This is just a wrapper for the `wcs_to_xy()` function, which in turn is a 
    wrapper for the Astropy `wcs.all_world2pix()` function.

    Note that although this function returns the table, it is modified in 
    place, so you don't need to catch the output.

    :param catalog: Table that has RA and Dec columns, whose names are specified
                    below.
    :type catalog: astropy.table.Table
    :param image_path: File path to the FITS image that will used to calculate 
                       the pixel values. 
    :type image_path: str
    :param ra_col: Name of the RA column in your `catalog`. Defaults to "ra".
    :type ra_col: str
    :param dec_col: Name of the Dec column in your `catalog`. Defaults to "dec".
    :type dec_col: str
    :param x_col: Name of the column holding the x values that will be created.
                  Defaults to "x".
    :type x_col: str
    :param y_col: Name of the column holding the y values that will be created.
                  Defaults to "y".
    :return: Catalog with the added x and y columns. Note that the table is 
             modified in place, so this isn't strictly necessary.
    :rtype: astropy.table.Table
    """
    x, y = wcs_to_xy(catalog["ra"], catalog["dec"], image_path)
    catalog[x_col] = x
    catalog[y_col] = y
    return catalog

def table_xy_to_wcs(catalog, image_path, x_col="x", y_col="y",
                    ra_col="ra", dec_col="dec"):
    """
    Adds RA/Dec columns to a table containig pixel locations.

    This function takes an astropy table with columns containing the x and y 
    values of the locations of your objects, and adds columns containing the 
    ra and dec of these objects in a given image. 

    This is just a wrapper for the `xy_to_wcs()` function, which in turn is a 
    wrapper for the Astropy `wcs.all_pix2world()` function.

    Note that although this function returns the table, it is modified in 
    place, so you don't need to catch the output.

    :param catalog: Table that has x and y columns, whose names are specified
                    below.
    :type catalog: astropy.table.Table
    :param image_path: File path to the FITS image that will used to calculate 
                       the pixel values. 
    :type image_path: str
    :param x_col: Name of the column holding the x values. Defaults to "x".
    :type x_col: str
    :param y_col: Name of the column holding the y values. Defaults to "y".
    :param ra_col: Name of the RA column that will be created. Defaults to "ra".
    :type ra_col: str
    :param dec_col: Name of the Dec column that will be created. Defaults 
                    to "dec".
    :type dec_col: str
    :return: Catalog with the added RA and Dec columns. Note that the table is 
             modified in place, so this isn't strictly necessary.
    :rtype: astropy.table.Table
    """
    ra, dec = xy_to_wcs(catalog[x_col], catalog[y_col], image_path)
    catalog[ra_col] = ra
    catalog[dec_col] = dec
    return catalog

def num_nearby(ras, decs, max_sep=5):
    """
    Calculate the number of objects that are within some separation.

    For each object, this calculates the number of objects within some distance
    on the sky. 

    See `table_num_nearby` if you have an astropy table with the ra/dec info.

    :param ras: list of RA values for all the objects.
    :type ras: list
    :param decs: list of Dec values for all the objects.
    :type decs: list
    :param max_sep: Maximum separation (in arcseconds) of two objects for 
                    them to be considered neighbors. 

    """
    # first turn our coordinates into SkyCoord objects, so we can get separation
    coords = SkyCoord(ras, decs, unit=u.degree)

    # initialize an array of the number of neighbors each object has
    neighbors = np.zeros(len(coords))

    # BASIC ALGORITHM
    # We will use the match_to_catalog_sky() function, which returns the 
    # separation of the nth closest object in the catalog. We will start at 2
    # (which is the closest object other than itself). For each object in the 
    # catalog, we will see if the nth match is within the required distance.
    # If it is, we will increment a counter.
    iteration = 2
    while True:
        idx, sep, dist = coords.match_to_catalog_sky(coords, iteration)
        # get an array where each entry is 1 if the match is within max_sep, and
        # zero if the match is not close enough. The greater than zero ignores
        # identical objects, if for some reason that are multiple identical
        # objects in the catalog
        close_enough = np.where(sep <= max_sep * u.arcsec, 
                                np.ones(len(coords)), np.zeros(len(coords)))
        
        # we then add this to neighbors, which basically increments the number
        # of nearby objects for the objects that have one this iteration
        neighbors += close_enough

        # continue until none of the objects have close matches.
        if not np.any(close_enough):
            return neighbors
        
        iteration += 1
    

def table_num_nearby(catalog, ra_col="ra", dec_col="dec", 
                     max_sep=5, num_nearby_col="num_nearby"):
    """ Wrapper for `num_nearby()` that supports astropy tables.
    
    See the `num_nearby()` documentation for more info.

    :param catalog: Astropy table object that holds ra/dec info.
    :type catalog: astropy.table.Table
    :param ra_col: name of the RA column in `catalog`.
    :type ra_col: str
    :param dec_col: name of the Dec column in `catalog`.
    :type dec_col: str
    :param max_sep: Maximum separation (in arcseconds) of two objects for 
                    them to be considered neighbors. Will be passed directly
                    to `num_nearby()`
    :type max_sep: float
    :param num_nearby_col: name of the column to add to the table with the
                           results of `num_nearby()`
    :type num_nearby_col: str
    :returns: None, but modifies the table 
    """
    
    catalog[num_nearby_col] = num_nearby(catalog[ra_col], catalog[dec_col],
                                         max_sep)
    
# TODO: make a scalar version of those nearby functions (ie where one location
#       is matched to a large catalog)
