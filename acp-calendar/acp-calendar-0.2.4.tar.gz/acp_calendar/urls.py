from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^working-days/(?P<start_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<end_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$",
        views.working_days, name="working_days"),
    url(r"^api/working-delta/(?P<start_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<days>[0-9]+)/$",
        views.working_delta, name="working_delta"),
    ]
