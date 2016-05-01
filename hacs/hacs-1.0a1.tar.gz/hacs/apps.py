# -*- coding: utf-8 -*-
import os
import sys
from django.conf import settings
from django.apps import AppConfig
from django.utils._os import safe_join
from django.utils.translation import ugettext_lazy as _

from .globals import HACS_APP_NAME
from .globals import HACS_APP_LABEL

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class HACSConfig(AppConfig):

    """
    """
    name = HACS_APP_NAME
    label = HACS_APP_LABEL
    verbose_name = _('Hybrid Access Control System')

    def ready(self):
        """
        :return:
        """
        _path = getattr(settings, 'HACS_GENERATED_URLCONF_DIR', safe_join(self.path, 'generated'))
        if not os.path.exists(_path):
            os.mkdir(_path)

        if _path not in sys.path:
            sys.path = sys.path[:] + [_path]

        return super(HACSConfig, self).ready()


