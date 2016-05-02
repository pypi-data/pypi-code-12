"""Pre-made model factories with mixer."""
from mixer.backend.django import mixer


def new_server_factory():
    """Returns a Server instance like it was just set up."""
    return mixer.blend(
        'server_guardian.Server',
        last_updated=None,
    )
