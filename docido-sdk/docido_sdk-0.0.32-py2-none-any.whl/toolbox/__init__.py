
from . text import to_unicode


def get_last_traceback():
    """Retrieve the last traceback as an `unicode` string."""
    import traceback
    from StringIO import StringIO
    tb = StringIO()
    traceback.print_exc(file=tb)
    return to_unicode(tb.getvalue())
