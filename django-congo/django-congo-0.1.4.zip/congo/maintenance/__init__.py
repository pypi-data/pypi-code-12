# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.utils.models import get_model

SITE_CACHE = {}
CONFIG_CACHE = {}

def get_current_site(request = None):
    if settings.CONGO_SITE_MODEL:
        model = get_site_model()
        return model.objects.get_current(request)
    return None

def get_site_model():
    return get_model('CONGO_SITE_MODEL')

def get_log_model():
    return get_model('CONGO_LOG_MODEL')

def get_cron_model():
    return get_model('CONGO_CRON_MODEL')

def get_audit_model():
    return get_model('CONGO_AUDIT_MODEL')

def get_admin_model():
    return get_model('CONGO_ADMIN_MODEL')
