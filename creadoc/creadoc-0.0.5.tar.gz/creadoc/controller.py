# coding: utf-8
from django.conf import settings
from m3.actions import ActionController

__author__ = 'damirazo <me@damirazo.ru>'


# Базовый контроллер для всех паков дизайнера отчетов
creadoc_controller = ActionController(
    url='/' + settings.CREADOC_URL,
)
