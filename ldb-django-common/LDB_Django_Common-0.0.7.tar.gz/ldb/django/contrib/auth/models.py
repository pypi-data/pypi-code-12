from django.db import models
from django.contrib.auth.models import User

class OwnedModel(models.Model):
    owner = models.ForeignKey(User)

    class Meta:
        abstract = True
