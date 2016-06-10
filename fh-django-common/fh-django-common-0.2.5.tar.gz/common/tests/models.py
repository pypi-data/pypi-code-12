from django.db import models

from common.models import DateTimeModelMixin


class TestDateTimeModel(DateTimeModelMixin):
    title = models.CharField(max_length=30)
