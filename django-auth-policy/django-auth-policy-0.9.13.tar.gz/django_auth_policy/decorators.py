from django_auth_policy.settings import LOGIN_NOT_REQUIRED_MARKER


def login_not_required(view):
    """Decorator to bypass LoginRequiredMiddleware for a view."""
    setattr(view, LOGIN_NOT_REQUIRED_MARKER, True)
    return view
