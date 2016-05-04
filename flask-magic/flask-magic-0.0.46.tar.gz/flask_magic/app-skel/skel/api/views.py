"""
Magic: API
"""

from flask_magic import (Magic, get_config, abort, request)
from flask_magic.decorators import (route, methods, render_as_json, render_as_xml)
from flask_magic.plugins import error_page


@render_as_json
def error_renderer(error):
    """
    Custom render output for API endpoint
    When abort() is invoked, it will render this function
    :param error: The error sent
    :return: dict
    """
    return {
        "error": True,
        "description": error.description,
        "code": error.code
    }, error.code
error_page.renderer = error_renderer


@render_as_json
class Index(Magic):
    """ API Endpoints """

    def index(self):
        return {
            "name": get_config("APPLICATION_NAME"),
            "version": get_config("APPLICATION_VERSION")
        }

    def get(self, id):
        return {
            "description": "This is a get",
            "id": id
        }

    def test(self, id):
        return {
            "desc": "This is a test",
            "id": id
        }

    def error(self):
        abort(400, "Custom Message")


