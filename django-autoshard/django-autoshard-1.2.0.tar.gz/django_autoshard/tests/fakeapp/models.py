from django.contrib.auth.models import AbstractUser

from django_autoshard.models import ShardedModel, ShardedManager


class User(ShardedModel, AbstractUser):
    SHARD_KEY = 'email'

    objects = ShardedManager()
