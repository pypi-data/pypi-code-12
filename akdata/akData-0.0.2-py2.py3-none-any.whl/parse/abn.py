import re


def parseAbn(abn):
    """Parses a string (possibly containing spaces) into an ABN (still a string but without spaces) and returns various error objects if invalid."""
    abn=abn.replace(' ','')
    if len(abn)<11:
        return parseAbn.TOO_SHORT
    if len(abn)>11:
        return parseAbn.TOO_LONG
    if not re.match('[0-9]+$',abn):
        return parseAbn.INVALID
    if isValidAbn(abn):
        return abn
    return parseAbn.INVALID
parseAbn.TOO_SHORT=object()
parseAbn.TOO_LONG=object()
parseAbn.INVALID=object()
parseAbn.POSSIBLE_ERRORS=[parseAbn.TOO_SHORT,parseAbn.TOO_LONG,parseAbn.INVALID]
