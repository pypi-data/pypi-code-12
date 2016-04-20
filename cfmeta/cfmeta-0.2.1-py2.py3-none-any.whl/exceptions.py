"""Module with custom exceptions for cfmeta.
"""

class PathError(Exception):
    def __init__(self, path):

        # Call the base class constructor with the parameters it needs
        super(PathError, self).__init__('File path {} does not match CMOR spec'.format(path))
