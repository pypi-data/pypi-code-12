from django.conf import settings

from vr.server.models import Swarm, Squad


def get_version(pkgname):
    import pkg_resources
    return pkg_resources.get_distribution(pkgname).version


def raptor(request):
    return {
        # For showing a list of all swarms in the nav
        'swarms': Swarm.objects.filter(),
        'squads': Squad.objects.all(),
        # Don't show web log links if syslogging is enabled
        'log_links': not settings.PROC_SYSLOG,
        'site_title': getattr(settings, 'SITE_TITLE', 'Velociraptor'),
        'custom_css': getattr(settings, 'CUSTOM_CSS', None),
        'max_events': getattr(settings, 'EVENTS_BUFFER_LENGTH', 100),
        'version': get_version('vr.server'),
    }
