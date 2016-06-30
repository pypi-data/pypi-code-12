from __future__ import unicode_literals

from django.db import models

# Create your models here.
class TestModel(models.Model):
    test = models.CharField(max_length=255)
    test3 = models.CharField(max_length=255)

    def __unicode__(self):
        return "test: %s test3: %s"%(test, test3)
