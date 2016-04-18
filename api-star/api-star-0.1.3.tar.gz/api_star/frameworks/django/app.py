from api_star.frameworks.django import urls
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
import django
import os


from django.conf.urls import url
from django.http import HttpResponse


def index(request):
    return HttpResponse('Hello World')


class App(WSGIHandler):
    def __init__(self):
        settings.configure(
            DEBUG=True,
            SECRET_KEY=os.urandom(32),
            ROOT_URLCONF='api_star.frameworks.django.urls',
            MIDDLEWARE_CLASSES=(),
        )
        django.setup()
        super(App, self).__init__()
        urls.urlpatterns = (
            url(r'^$', index),
        )

app = App()
