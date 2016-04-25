import urllib
import urllib2

from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string

from . import app_settings
from .utils import from_dotted_path

backend_fn = from_dotted_path(app_settings.BACKEND)

def hipchat_message(template, context=None, fail_silently=app_settings.FAIL_SILENTLY):
    context = Context(context or {})

    context['settings'] = settings

    def render(component):
        component_template = 'django_hipchat/%s' % component

        return render_to_string(template, {
            'django_hipchat': component_template,
        }, context).strip().encode('utf8', 'ignore')

    data = {
        'from': app_settings.MESSAGE_FROM,
        'color': 'yellow',
        'message': '',
        'room_id': app_settings.MESSAGE_ROOM,
        'auth_token': app_settings.AUTH_TOKEN,
        'message_format': 'html',
    }

    for part in ('auth_token', 'room_id', 'message', 'color', 'from'):
        try:
            txt = render(part)
        except Exception:
            if fail_silently:
                return
            raise

        if txt:
            data[part] = txt

    for x in ('auth_token', 'from', 'message', 'room_id'):
        if data[x]:
            continue

        if fail_silently:
            return

        assert False, "Missing or empty required parameter: %s" % x

    backend_fn('%s?%s' % (
        'https://api.hipchat.com/v1/rooms/message',
        urllib.urlencode(data),
    ), data, fail_silently)
