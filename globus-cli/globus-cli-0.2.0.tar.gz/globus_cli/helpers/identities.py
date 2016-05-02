import re

# what qualifies as a valid Identity Name?
_IDENTITY_NAME_REGEX = '^[a-zA-Z0-9]+.*@[a-zA-z0-9-]+\..*[a-zA-Z]+$'


def is_valid_identity_name(identity_name):
    """
    Check if a string is a valid identity name.
    Does not do any preprocessing of the identity name, so you must do so
    before invocation.
    """
    if re.match(_IDENTITY_NAME_REGEX, identity_name) is None:
        return False
    else:
        return True
