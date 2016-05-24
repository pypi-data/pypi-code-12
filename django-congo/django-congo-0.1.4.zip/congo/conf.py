# -*- coding: utf-8 -*-
from appconf import AppConf
from django.conf import settings as django_settings
from django.core.cache import DEFAULT_CACHE_ALIAS
from django.utils.translation import ugettext_lazy as _
import os

settings = django_settings

class CongoAppConf(AppConf):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # sites

    SITE_MODEL = None # eg 'maintenance.Site'

    # logs

    LOG_MODEL = None # eg 'maintenance.Log'
    LOG_ROOT = os.path.join(settings.BASE_DIR, 'logs')
    COMMON_ERRORS_IGNORE_LIST = []

    # audit

    AUDIT_MODEL = None # eg 'maintenance.Audit'
    TEST_MODULE = None # eg 'maintenance.tests'
    TEST_CHOICE_PATH = None # eg os.path.join(BASE_DIR, *JOBS_MODULE.split('.'))

    # cron

    CRON_MODEL = None # eg 'maintenance.Cron'
    JOBS_MODULE = None # eg 'maintenance.jobs'
    JOB_CHOICE_PATH = None # eg os.path.join(BASE_DIR, *JOBS_MODULE.split('.'))

    # url redirects

    URL_REDIRECT_MODEL = None # eg 'maintenance.UrlRedirect'

    # cache

    TEMPLATE_CACHE_BACKEND = DEFAULT_CACHE_ALIAS # eg 'template_cache'

    # admin

    ADMIN_MODEL = 'congo.admin.admin.BaseModelAdmin'
    ADMIN_PATH = '/admin/'
    ADMIN_LANGUAGE_CODE = settings.LANGUAGE_CODE

    # accounts

    SSL_ENABLED = False
    AUTHENTICATION_DOMAIN = (lambda: settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) else 'example.com')()

    # external

    GOOGLE_BROWSER_API_KEY = None

    # secure

    SSL_ENABLED = False
    IGNORABLE_SSL_URLS = ()

    # communication

    DEFAULT_FROM_EMAIL_NAME = None

    EMAIL_PREMAILER_BASE_PATH = settings.BASE_DIR
    EMAIL_TEMPLATE_DOMAIN = (lambda: settings.ALLOWED_HOSTS[0] if len(settings.ALLOWED_HOSTS) else 'www.example.com')() # domain used as placeholder in e-mail templates

    EMAIL_SENDER_MODEL = None # eg 'communication.EmailSender'
    EMAIL_RECIPIENT_GROUP_MODEL = None # eg 'communication.EmailRecipientGroup'
    EMAIL_RECIPIENT_MODEL = None # eg 'communication.EmailRecipient'
    EMAIL_MESSAGE_MODEL = None # eg 'communication.EmailMessage'
    EMAIL_MESSAGE_QUEUE_MODEL = None # eg 'communication.EmailMessageQueue'

    SMS_RECIPIENT_GROUP_MODEL = None # eg 'communication.SMSRecipientGroup'
    SMS_RECIPIENT_MODEL = None # eg 'communication.SMSRecipient'
    SMS_MESSAGE_MODEL = None # eg 'communication.SMSMessage'
    SMS_MESSAGE_QUEUE_MODEL = None # eg 'communication.SMSMessageQueue'

    SMS_SENDER_LIST = (
        ('ECO', _("Random number")),
    )
    SMS_BACKEND = 'congo.communication.backends.console.SMSBackend' # eg 'congo.communication.backends.smsapi.SMSBackend'
    SMSAPI_USER = '' # eg 'user'
    SMSAPI_PASSWORD = '' # eg 'abc123'

    # gallery

    BLANK_IMAGE_FILENAME = 'blank_image.jpg'
    BLANK_IMAGE_PATH = os.path.join(settings.STATIC_ROOT, 'img', 'blank_image')
    BLANK_IMAGE_URL = '/static/img/blank_image/'

    WATERMARK_PATH = os.path.join(settings.STATIC_ROOT, 'img', 'watermarks')

    DEFAULT_IMAGE_WIDTH = 800
    DEFAULT_IMAGE_HEIGHT = 800

    WATERMARK_MIN_WIDTH = 500
    WATERMARK_MIN_HEIGHT = 500

    # meta class

    DEFAULT_META_TITLE = "Congo Project"
    DEFAULT_META_DESCRIPTION = "Tools for faster and more efficient Django application developing"
    DEFAULT_META_IMAGE = ""
