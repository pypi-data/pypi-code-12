from django.contrib.sites.models import Site
from django.db import models
from model_utils.models import TimeStampedModel


class URLStatusLog(TimeStampedModel):
    site = models.ForeignKey(Site)
    url = models.URLField(help_text='The URL which was called - '
                          '`site.domain`.')
    site_is_up = models.BooleanField()
    latest_update = models.DateTimeField()