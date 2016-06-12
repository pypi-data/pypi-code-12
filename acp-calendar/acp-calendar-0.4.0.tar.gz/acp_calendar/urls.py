from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^api/', include('acp_calendar.api.urls', namespace='calendar-api')),
    ]
