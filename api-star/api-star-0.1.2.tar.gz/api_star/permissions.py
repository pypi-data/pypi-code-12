# Note: We parameterize these permissions for consistency with the
# rest of the API, although they do not actually take any arguments.


def is_authenticated():
    def has_permission(request):
        return bool(request.auth)
    return has_permission


def is_authenticated_or_read_only():
    def has_permission(request):
        return (
            bool(request.auth) or
            request.method in ('GET', 'HEAD', 'OPTIONS')
        )
    return has_permission
