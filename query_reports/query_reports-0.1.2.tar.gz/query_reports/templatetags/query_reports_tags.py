from django import template
from django.conf import settings

register = template.Library()


@register.filter
def get(obj, attr, default=None):
    if obj is None:
        return default
    elif isinstance(obj, (tuple, list)):
        return obj[attr]
    elif isinstance(obj, dict):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)


@register.filter
def pages(page, span=5):
    paginator = page.paginator

    pages = []
    if page.has_other_pages():

        max = span*2 + 1
        lower_span = page.number - span
        if max > paginator.num_pages:
            lower_span -= max - paginator.num_pages
            max = paginator.num_pages

        if lower_span <= 1:
            lower_span = 1
        else:
            pages += [None]

        for idx in range(max):
            try:
                pages += [paginator.page(lower_span + idx)]
            except:
                pass

        if lower_span + max <= paginator.num_pages:
            pages += [None]

    return pages


@register.simple_tag
def embed(filename):
    replace = ""
    if settings.STATIC_URL in filename:
        root = settings.STATIC_ROOT
        replace = settings.STATIC_URL
    elif settings.MEDIA_URL in filename:
        root = settings.MEDIA_ROOT
        replace = settings.MEDIA_URL

    if not root.endswith("/"):
        root += "/"
    filename = filename.replace(replace, root)

    fileh = open(filename, "r")
    retval = fileh.read()
    fileh.close()

    return retval
