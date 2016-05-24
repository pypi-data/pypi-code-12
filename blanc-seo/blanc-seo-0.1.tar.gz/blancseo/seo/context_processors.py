from django.utils.functional import SimpleLazyObject
from django.conf import settings
from blancseo.seo.models import URLMetaContent


def url_metacontent(request):
    def get_metacontent():
        url = request.path_info

        # This has no chance of working
        if not url.endswith('/') and settings.APPEND_SLASH:
            return ''

        if not url.startswith('/'):
            url = '/' + url

        try:
            return URLMetaContent.objects.get(url=url)
        except URLMetaContent.DoesNotExist:
            return ''

    return {
        'url_metacontent': SimpleLazyObject(get_metacontent),
    }
