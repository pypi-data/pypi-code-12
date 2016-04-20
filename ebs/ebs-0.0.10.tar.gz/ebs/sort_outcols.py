"""Returns the desired order of the columns in the new dataframe.

Uses the fact that the the number of original columns in the header is
len(header) - [len(outindexes) | len(merge_on_cols); those are the new columns

Arguments:
outindexes    -- the positions to insert the new data
header        -- the header with new columns inserted
merge_on_cols -- the names of the columns to join on"""

def get_final_outcolumn_order(outindexes, header, merge_on_cols):

    nb_new_cols = len(merge_on_cols) or len(outindexes)
    old_header, new_header = header[:-nb_new_cols], header[-nb_new_cols:]

    if outindexes:
        outindexes = _correct_outpositions(outindexes)
    else:
        outindexes = _find_outindexes(header, merge_on_cols)
        outindexes = _correct_outpositions(outindexes)
        outindexes = [i + 1 for i in outindexes]


    for i, out_ix in enumerate(outindexes):
        old_header.insert(out_ix, new_header[i])

    return old_header


def _correct_outpositions(outindexes):

    """Finds the correct indexes to insert on if user supplied outcols as int.

    if a and b should be inserted in position 0 and 5 in the original array
    bs index must be increased by 1 after a is inserted and so on."""

    proper_outindexes = [i + c for i, c in enumerate(outindexes)]

    return proper_outindexes


def _find_outindexes(header, merge_on_cols):

    """Finds the correct indexes to insert on if user supplied column names."""
    outindexes = []
    for merge_col in merge_on_cols:
        for i, header_col in enumerate(header):
            if merge_col == header_col:
                outindexes.append(i)

    return outindexes
