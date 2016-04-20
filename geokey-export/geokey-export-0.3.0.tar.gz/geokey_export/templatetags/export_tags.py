from django import template
from django.template.defaultfilters import date as filter_date

register = template.Library()


@register.filter(name='expiry')
def expiry(export):
    if export.isoneoff:
        return 'One off'
    elif export.expiration:
        return filter_date(export.expiration, 'd F, Y H:i')
    else:
        return 'Never'
