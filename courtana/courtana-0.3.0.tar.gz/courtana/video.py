import logging
import os
import re


FILENAME_PATTERN = re.compile(
        r"^(?P<date>\d{8})"                     # date
        r"(?:_(?P<female>[a-zA-Z0-9-]+[^_]))?"  # female info
        r"(?:_(?P<male>[a-zA-Z0-9-]+[^_]))?"    # male info
        r"(?:_(?P<info>[a-zA-Z0-9-]+[^_]))?"    # additional info
        r"(?:_(?P<id>\d+))?"                    # video ID
        r"(?:_(?P<extra>[a-zA-Z0-9-]+[^_]))?"   # extra info
        r"(?:\.(?P<ext>\w+))$"                  # file extension
    )

FILENAME_PATTERN_GROUPS = [
    group
    for group in FILENAME_PATTERN.groupindex.keys()
    if group != 'ext'
]


log = logging.getLogger(__name__)


class FileName:
    """
    Supports video files whose names contain information about the
    acquisition parameters.
    """

    def __init__(self, filepath=None, **fields):

        if not any(fields):
            if filepath is None:
                raise ValueError("Arguments are invalid")
            if not isinstance(filepath, str):
                fields = filepath
                filepath = None

        # Populate class attributes from regex groups
        for group_name in FILENAME_PATTERN_GROUPS:
            setattr(self, group_name, '')

        if filepath is None:
            self.filepath = None
            self.filename = None
        else:
            self.filepath = filepath
            self.filename = os.path.basename(filepath)
            fields = self._parse()

        self.__dict__.update(self._validade_fields(fields))

        log.debug(self.__dict__)

    def _validade_fields(self, fields):
        """Validates the fields dictionary, removing the invalid keys.
        """
        validated_fields = {}
        for field, value in fields.items():
            if field in FILENAME_PATTERN_GROUPS:
                validated_fields[field] = value
            else:
                log.warning("Ignoring invalid field '%s'" % field)
        return validated_fields

    def _parse(self):
        """Parse the video file name and returns a dict with the matches.
        Raises a ValueError if the matching fails.
        """
        log.debug("Parsing filename '%s'" % self.filename)
        match = re.fullmatch(FILENAME_PATTERN, self.filename)
        if match:
            matches = match.groupdict(default='')
            del matches['ext']
        else:
            raise ValueError("Invalid filename: regex matching failed")
        log.debug("Parser results: %s" % matches)
        return matches

    def fields(self):
        """Return the fields dictionary characteriing the video.
        """
        return {
            key: value
            for key, value in self.__dict__.items()
            if key in FILENAME_PATTERN_GROUPS
        }
