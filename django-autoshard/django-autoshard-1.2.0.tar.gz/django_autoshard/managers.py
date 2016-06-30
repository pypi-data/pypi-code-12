from django.contrib.auth import get_user_model
from django.db import models

from django_autoshard.querysets import ShardedQuerySet


class ShardedManager(models.Manager):
    _queryset_class = ShardedQuerySet

    def all(self):
        return self.filter()


class UserManager(ShardedManager):
    def create_user(self, username, email, password=None, save=True):  # pragma: no cover
        user = get_user_model()(
            username=username,
            email=email)
        user.set_password(password)
        if save:
            user.save()
        return user

    def create_superuser(self, username, email, password):  # pragma: no cover
        user = self.create_user(username, email, password, False)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

