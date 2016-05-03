# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from .models import Notification


def create_notification(target, **kwargs):
    return Notification.objects.create(target=target, **kwargs)
