from django.conf.urls import url
from congo.conf import settings

urlpatterns = []

if settings.CONGO_CRON_MODEL:
    urlpatterns += [
        url(r'^cron/(?P<cron_id>[\d])/$', 'congo.maintenance.views.cron', name = "congo_maintenance_cron"),
    ]

if settings.CONGO_EMAIL_MESSAGE_MODEL:
    urlpatterns += [
        url(r'^preview-email/(?P<message_id>[\d])/$', 'congo.communication.views.preview_email', name = "congo_communication_maintenance_cron"),
    ]

