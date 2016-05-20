# -*- coding: utf-8 -*-
from django.conf import settings as site_settings


DEFAULT_SETTINGS = {
    'CLICK_THROUGH_TEMPLATE': '<p><a target="_blank" href="%s">Read more <i class="ng-icon-angle-double-right"></i></a></p>',
    'BACKGROUND_IMAGE_RELATED_FIELD': 'image'
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(site_settings, 'TIMELINES_SETTINGS', {}))

globals().update(USER_SETTINGS)
