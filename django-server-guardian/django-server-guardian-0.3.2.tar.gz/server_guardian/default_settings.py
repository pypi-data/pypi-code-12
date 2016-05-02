"""Default settings for the app."""
from django.conf import settings

EMAIL_ON_STATUS = getattr(
    settings,
    'SERVER_GUARDIAN_EMAIL_ON_STATUS',
    [403, 404, 405],
)


DASHBOARD_VIEW_PERMISSION = getattr(
    settings,
    'SERVER_GUARDIAN_DASHBOARD_VIEW_PERMISSION',
    lambda u: u.is_superuser
)
