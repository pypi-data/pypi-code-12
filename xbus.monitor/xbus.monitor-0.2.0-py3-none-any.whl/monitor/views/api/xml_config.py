from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.view import view_config

from ...utils.xml_config import load_config


@view_config(
    route_name='xml_config',
    request_method='GET',
    renderer='json',
)
def xml_config_read(request):
    # TODO Implement.
    raise HTTPNotImplemented(json_body={})


@view_config(
    route_name='xml_config',
    request_method='PUT',
    renderer='json',
)
def xml_config_update(request):
    try:
        xml = request.json_body['xml']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    load_config(xml)

    # TODO Implement.
    return {}
