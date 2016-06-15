# coding: utf-8
from django.conf.urls import patterns
from m3_users import GENERIC_USER
from m3_users.metaroles import UserMetarole
from demo.app import controller
from demo.app.metaroles import CREADOC_DEMO_METAROLE

__author__ = 'damirazo <me@damirazo.ru>'


def register_urlpatterns():
    return patterns(
        '',
        ('^', controller.action_controller.process_request),
    )


def register_metaroles(manager):
    manager.CREADOC_DEMO_METAROLE = UserMetarole(
        CREADOC_DEMO_METAROLE,
        u'Демонстрационный пользователь'
    )

    manager.GENERIC_METAROLE = UserMetarole(
        GENERIC_USER,
        u'Обобщенный пользователь'
    )

    return [
        manager.CREADOC_DEMO_METAROLE,
        manager.GENERIC_METAROLE,
    ]
