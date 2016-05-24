from django.db import models

class ClassA(models.Model):
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=40, null=False, blank=False)
    description.service = 'algumservico'
    teste = ''
