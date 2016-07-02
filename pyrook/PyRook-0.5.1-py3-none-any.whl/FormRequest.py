

from .Importer.QtNetwork import *



class FormRequest(QNetworkRequest):
    """Convenience function that automatically sets MIME type header for form
    post requests."""
    def __init__(self, *args, **kwargs):
        QNetworkRequest.__init__(self, *args, **kwargs)
        self.setHeader(QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded")
