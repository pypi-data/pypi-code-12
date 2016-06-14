from django.db import models


class InvalidUser(models.Model):
    username = models.CharField(max_length=256)
    failed_login_attempts = models.IntegerField(default=0)
