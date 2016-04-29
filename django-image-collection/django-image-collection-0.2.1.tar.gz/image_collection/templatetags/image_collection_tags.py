"""Templatetags for the image_collection app."""
from distutils.version import StrictVersion

from django import get_version, template

from ..models import ImageCollection


register = template.Library()


django_version = get_version()
if StrictVersion(django_version) < StrictVersion('1.9'):
    filename = 'file_name'
else:
    filename = 'filename'

tag_kwargs = {
    'takes_context': True,
    filename: 'image_collection/tags/bs3_carousel.html'
}


@register.inclusion_tag(**tag_kwargs)
def render_bs3_carousel(context, identifier):
    """Renders an image collection as Bootstrap 3 carousel."""
    try:
        collection = ImageCollection.objects.get(identifier=identifier)
    except ImageCollection.DoesNotExist:
        collection = None
    context.update({'collection': collection})
    return context
