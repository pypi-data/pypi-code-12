from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.conf import settings
from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy


class PersonaMiddleware(object):

    def process_request(self, request):
        site = Site.objects.get(is_default_site=True)
        setting = SettingsProxy(site)
        persona_settings = setting['usermetadata']['PersonaeSettings']

        if not persona_settings.persona_required:
            return None

        exclude = [
            settings.MEDIA_URL,
            settings.STATIC_URL,
            reverse('molo.usermetadata:persona'),
            reverse('health'),
            reverse('versions'),
            '/admin/',
            'django-admin/',
            '/import/',
            '/locale/'
        ]

        if hasattr(settings, 'PERSONA_IGNORE_PATH'):
            exclude += settings.PERSONA_IGNORE_PATH

        if any([p for p in exclude if request.path.startswith(p)]):
            return None

        if 'MOLO_PERSONA_SELECTION' not in request.session:
            url = '%s?next=%s' % (reverse('molo.usermetadata:persona'),
                                  request.path)
            return redirect(url)
