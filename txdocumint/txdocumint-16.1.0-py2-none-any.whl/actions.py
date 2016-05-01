"""
Documint action factories.

Each public function produces a `dict` suitable for passing to the
`perform_action` session method.
"""


def _action(name, params):
    """
    Convenience function for constructing an action `dict`.
    """
    return {u'action': name,
            u'parameters': params}


def render_html(input, base_uri=None):
    """
    Render an HTML document to a PDF document.

    :param unicode input: URI to the HTML content to render.
    :param base_uri: Optional base URI to use when resolving relative URIs.
    :type base_uri: unicode or None
    """
    def _parse_render(result):
        return result[u'links'][u'result'][0]
    params = {u'input': input}
    if base_uri is not None:
        params[u'base-uri'] = base_uri
    return _action(u'render-html', params), _parse_render


def concatenate(inputs):
    """
    Concatenate several PDF documents together.

    :param inputs: Document URIs.
    :type inputs: list of unicode
    """
    def _parse_concat(result):
        return result[u'links'][u'result'][0]
    return _action(u'concatenate',
                   {u'inputs': inputs}), _parse_concat


def thumbnails(input, dpi):
    """
    Generate JPEG thumbnails for a PDF document.

    :param unicode input: Document URI.
    :param int dpi: Pixel density of the thumbnail.
    """
    def _parse_thumbnails(result):
        return result[u'links'][u'results']
    return _action(u'thumbnails',
                   {u'input': input,
                    u'dpi': dpi}), _parse_thumbnails


def split(input, page_groups):
    """
    Split a PDF document into multiple PDF documents.

    :param unicode input: Document URI.
    :param page-groups: Page number groups, each group of pages represents a
    new document containing only those pages from the original document in the
    order they are specified. For example ``[[1, 3, 2], [4, 2]]`` produces two
    documents: one with pages 1, 3 and 2; the other with pages 4 and 2.
    :type page-groups: list of lists of int
    """
    def _parse_split(result):
        return result[u'links'][u'results']
    return _action(u'split',
                   {u'input': input,
                    u'page-groups': page_groups}), _parse_split


def metadata(input):
    """
    Retrieve metadata from a PDF document.

    :param unicode input: Document URI.
    """
    def _parse_metadata(result):
        return result[u'body']
    return _action(u'metadata',
                   {u'input': input}), _parse_metadata


def sign(inputs, certificate_alias, location, reason):
    """
    Digitally sign one or more PDF documents.

    :param inputs: Document URIs.
    :type inputs: list of unicode
    :param unicode certificate_alias: Certificate alias, in the Documint
    keystore, to use when signing the documents.
    :param unicode location: Signing location.
    :param unicode reason: Signing reason.
    """
    def _parse_sign(result):
        return result[u'links'][u'results']
    return _action(u'sign',
                   {u'inputs': inputs,
                    u'certificate-alias': certificate_alias,
                    u'location': location,
                    u'reason': reason}), _parse_sign


def crush(input, compression_profile):
    """
    Compress a PDF document according to a specific compression profile.

    :param unicode input: Document URI.
    :param unicode compression_profile: Compression profile to use, possible
    choices are: ``text`` (bilevel), ``photo-grey`` (greyscale), ``photo``
    (colour).
    """
    def _parse_crush(result):
        return result[u'links'][u'result'][0]
    return _action(u'crush',
                   {u'input': input,
                    u'compression-profile': compression_profile}), _parse_crush
