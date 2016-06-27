from pyramid import security
from pyramid.renderers import get_renderer

from xbus.monitor.i18n import req_l10n


def get_view_params(request, title):
    """Fill parameters used by every view."""

    _ = req_l10n(request)

    login = security.authenticated_userid(request)

    return {
        'context_url': request.path_qs,
        'login': login,
        'macros': (
            get_renderer('xbus.monitor:templates/base.pt')
            .implementation().macros
        ),
        'project': _('Xbus Monitor'),
        'view_title': title,
    }
