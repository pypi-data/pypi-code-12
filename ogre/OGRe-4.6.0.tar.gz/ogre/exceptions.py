"""
OGRe Error Handler

:class:`OGReError` -- retriever error template

:class:`OGReLimitError` -- retriever limit error template
"""


class OGReError(Exception):

    """Create exceptions that contain an origin reference and a message."""

    def __init__(self, source="unknown", message="error"):
        super(OGReError, self).__init__()
        self.source = source
        self.message = message

    def __str__(self):
        return self.source+": "+self.message


class OGReLimitError(OGReError):

    """Supplement OGReError with a reset timestamp."""

    def __init__(self, source="unknown", message="error", reset=None):
        super(OGReLimitError, self).__init__(source, message)
        self.reset = reset
