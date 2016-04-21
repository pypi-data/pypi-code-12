#coding=utf-8
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import AbstractUser


class ModelEmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = get_user_model().objects.get(email=username)

            if user.check_password(password):
                return user
        except AbstractUser.DoesNotExist:
            return None
