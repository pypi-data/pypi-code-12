class InvalidIUPACAmbiguityCodeError(KeyError):
    """Indicated that a sequence contains a key-code which is not part
    of the set {A, C, G, T, ..., N}
    """

    def __init__(self, key_error):
        self.key = key_error.args[0]

    def __str__(self):
        return "Invalid sequence element {}. Only IUPAC ambiguity codes are allowed.".format(str(self.key))

class InvalidLinetypeError(ValueError):
    """Raised by FastqReader when a line cannot be typed as
    name, sequence, plus or quality values.
    """
    pass


class ChromosomeFormatError(ValueError):
    """Raised if a wrong format for a chromosome_info item is encountered
    by FastaWriter."""
    pass


class InvalidStartingCharacterError(ValueError):
    """Raised by Shape, if the shape string doesn't start with a
    valid character.
    """
    pass


class TooManyCharactersError(ValueError):
    """Raised by Shape, if the shape string contains more than two
    different characters.
    """
    pass

class UnknownCharactersError(ValueError):
    """Raised by Shape, if the shape string contains charcters other than #, - or _
    """
    pass


class InvalidDtypeError(ValueError):
    """Exception raised for invalid dtypes.

    Normally dtype should be on of:

    - str
    - bytes
    - bytearray
    - dinopy.basenumbers

    For details please see :ref:`dtype`.
    """
    pass


class InvalidEncodingError(ValueError):
    """Exception raised for invalid encoding type.

    Encoding should be one of:

    - dinopy.two_bit
    - dinopy.four_bit

    For details please see :ref:`dtype`.
    """
    pass
