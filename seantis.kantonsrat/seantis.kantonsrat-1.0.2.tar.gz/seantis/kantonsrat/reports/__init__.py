from collections import OrderedDict
from seantis.kantonsrat import _
from .organizations import InactiveOrganizationsReport, OrganizationsReport


#
# xxx replace with named adapters if this is going to be used more extensively
#
def get_available_reports(include_inactive=False):
    reports = OrderedDict()
    reports['organizations_with_members'] = {
        'title': _(u'Commissions-Report as PDF'),
        'description': _(
            u'Contains the members grouped by comission'
        ),
        'class': OrganizationsReport
    }
    if include_inactive:
        reports['inactive_organizations_with_members'] = {
            'title': _(u'Commissions-Report (inactive) as PDF'),
            'description': _(
                u'Contains the members grouped by comission'
            ),
            'class': InactiveOrganizationsReport
        }
    return reports
