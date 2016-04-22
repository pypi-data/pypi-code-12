from api_star.compat import string_types, text_type
from api_star.exceptions import Forbidden


def check_permissions(request, permissions):
    for permission in permissions:
        if not permission(request):
            raise Forbidden()


def render(request, data):
    """
    Given the incoming request, and the outgoing data,
    determine the content type and content of the response.
    """
    renderer = request.renderer or request.renderers[0]

    if data is None:
        content = b''
    elif not isinstance(data, string_types):
        context = {'request': request}
        content = renderer(data, **context)
    else:
        content = data

    if isinstance(content, text_type) and renderer.charset:
        content = content.encode(renderer.charset)

    if renderer.media_type:
        content_type = '%s' % renderer.media_type
        if renderer.charset:
            content_type += '; charset=%s' % renderer.charset
    else:
        content_type = None

    return (content, content_type)
