"""kvcomcon: key-value-comment config.

Example:

    # My cool config
    foo = bar
    sentence = This is my cool sentence.

The config format is line-based. Each line must be one of these:

1. A comment line (the first non-whitespace character is '#'
2. An empty line (whitespace is allowed)
3. somekey = somevalue

Leading and trailing whitespace is stripped from each line, as well as
around each key and value. For example, these two lines are equivalent:
    "key=val 123"
    "  key  = val 123     "
"""

class ConfigError(Exception):
    """Error while parsing configuration."""
    def __init__(self, line, line_number, filename):
        message = 'error parsing {} line {}'.format(filename, line_number)

        super(ConfigError, self).__init__(message)
        self.line = line
        self.line_number = line_number
        self.filename = filename


def parse_line(line, line_number, filename):
    """Parse a single line of a config file.

    Returns either a (key, value) pair or None.
    """
    line = line.strip()

    # Ignore empty lines
    if len(line) == 0:
        return None

    # Ignore comments
    if line.startswith('#'):
        return None

    maxsplits = 1
    parts = line.split('=', maxsplits)

    if len(parts) == 2:
        key = parts[0].strip()
        value = parts[1].strip()
        return (key, value)
    else:
        raise ConfigError(line, line_number, filename)


def config_from_fileobj(fileobj):
    """Parse a config from an object with a |readlines| method.

    This is a generator. It yields (key, value) pairs.
    """
    filename = getattr(fileobj, 'name', None)
    for line_number, line in enumerate(fileobj.readlines()):
        pair = parse_line(line, line_number + 1, filename)
        if pair is not None:
            yield pair


def config_from_path(path):
    """Parse a config from a file at |path|."""
    with open(path, 'r') as fileobj:
        for line in config_from_fileobj(fileobj):
            yield line
