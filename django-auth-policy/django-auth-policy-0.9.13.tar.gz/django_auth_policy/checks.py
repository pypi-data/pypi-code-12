from django.conf import settings
from django.core import checks


@checks.register('authpolicy')
def check_middleware(app_configs, **kwargs):
    errors = []
    middle = 'django_auth_policy.middleware.AuthenticationPolicyMiddleware'
    m_classes = tuple(settings.MIDDLEWARE_CLASSES)

    if middle not in m_classes:
        errors.append(checks.Critical(
            msg=('AuthenticationPolicyMiddleware is missing'),
            hint=('Add {} to MIDDLEWARE_CLASSES'.format(middle)),
            id='django_auth_policy.C001',
        ))

    return errors
