from django import template
from django.conf import settings
from django.core.urlresolvers import reverse

register = template.Library()


@register.inclusion_tag('pagetimer/pagetimer.html', takes_context=True)
def pagetimer(context):
    interval = 60
    if hasattr(settings, 'PAGETIMER_INTERVAL'):
        interval = settings.PAGETIMER_INTERVAL
    return {
        'pagetimer_endpoint': reverse('pagetimer-endpoint'),
        'pagetimer_interval': interval,
    }
