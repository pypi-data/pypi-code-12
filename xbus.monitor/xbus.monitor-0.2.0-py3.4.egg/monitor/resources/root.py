from pyramid import security


class RootFactory(object):
    """Default factory that allows any authenticated user to access our views.
    All views under the URL dispatch system use this root factory.
    """

    __acl__ = [
        (security.Allow, security.Authenticated, 'view'),
    ]

    def __init__(self, request):
        """Empty on purpose - this is needed to avoid errors."""
        pass
