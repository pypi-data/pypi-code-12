
from user_agents import parse

from . import settings


def verify_browser(request, min_versions=None):
    """ accepts a request and tags it with browser support info

        if `min_versions` is passed in, it skould be a dictionary of
            'browser': version
    """
    if not min_versions:
        min_versions = settings.MIN_BROWSER_VERSIONS

    request.user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
    request.browser_unknown = True
    request.browser_unsupported = False

    for family, version in min_versions.items():
        if request.user_agent.browser.family == family:
            request.browser_unknown = False

            bversion = request.user_agent.browser.version
            if isinstance(bversion, (list, tuple)):
                if len(bversion) > 0:
                    bversion = bversion[0]
                else:
                    bversion = 0
            else:
                bversion = bversion

            if bversion < version:
                request.browser_unsupported = True

            break
