from astropy.coordinates import match_coordinates_sky, SkyCoord
from astropy import units as u
from astropy import table
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
            
    matches.add_column(table.Column(data=sep * u.arcsec, name="sep [arcsec]"))

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
            
#TODO: write wrappers for the astropy join stuff