"""Template tags for the ``outlets`` app."""
from django import template

from .. import models

register = template.Library()


@register.assignment_tag
def get_outlet_countries():
    """Returns a list of outlet countries."""
    return models.OutletCountry.objects.all()
