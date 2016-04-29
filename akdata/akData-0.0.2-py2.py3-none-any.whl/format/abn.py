def formatAbn(abn):
    """Formats a string of numbers (no spaces) into an ABN."""
    if len(abn)!=11:
        return abn
    return u'{0} {1} {2} {3}'.format(abn[0:2],abn[2:5],abn[5:8],abn[8:11])
