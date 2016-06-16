import re


def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    return re.sub("[^a-zA-Z\d:]", text.lower(), "-")
