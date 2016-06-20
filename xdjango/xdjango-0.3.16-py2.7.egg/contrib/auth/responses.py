from rest_framework.response import Response as DRFResponse


INVALID_CREDENTIALS_ERROR_MSG = "Invalid credentials"


class Response(DRFResponse):
    """
    An HttpResponse that allows its data to be rendered into
    arbitrary media types and errors are encapsulated into a json object.
    """

    def __init__(self, data=None, status=None, template_name=None, headers=None, exception=False, content_type=None,
                 error=None):

        if data is None and error is None:
            data_error = None
        elif data is None:
            data_error = {"error": error}
        elif error is None:
            data_error = {"data": data}
        else:
            data_error = {"data": data, "error": error}

        super(Response, self).__init__(data=data_error, status=status, template_name=template_name, headers=headers,
                                       content_type=content_type, exception=exception)
