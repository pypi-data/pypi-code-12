from __future__ import unicode_literals

import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import management
from django.db import models
from django.utils.translation import ugettext_lazy as _

from solo.models import SingletonModel

from .settings import EMAIL, PASSWORD, USERNAME

logger = logging.getLogger(__name__)


class AutoAdminSingletonManager(models.Manager):
    def create_autoadmin(self):
        UserModel = get_user_model()

        # Get an usable password before creating the superuser
        if PASSWORD():
            try:
                # Let's try to see if it is a callable
                password = PASSWORD()()
            except TypeError:
                password = PASSWORD()
        else:
            password = UserModel.objects.make_random_password()

        try:
            UserModel.objects.get(**{UserModel.USERNAME_FIELD: USERNAME()})
        except UserModel.DoesNotExist:
            logger.info(
                'Creating superuser -- login: %s, email: %s, password: %s',
                USERNAME(), EMAIL(), password
            )
            management.call_command(
                'createsuperuser',
                **{
                    UserModel.USERNAME_FIELD: USERNAME(),
                    'email': EMAIL(),
                    'interactive': False
                }
            )

            account = UserModel.objects.get(
                **{UserModel.USERNAME_FIELD: USERNAME()}
            )
            account.set_password(raw_password=password)
            account.save()
            # Store the auto admin password properties to display the
            # first login message
            auto_admin_properties, created = AutoAdminSingleton.objects.get_or_create()  # NOQA
            auto_admin_properties.account = account
            auto_admin_properties.password = password
            auto_admin_properties.password_hash = account.password
            auto_admin_properties.save()
        else:
            logger.error(
                'Super admin user already exists. -- login: %s', USERNAME()
            )


class AutoAdminSingleton(SingletonModel):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        verbose_name=_('Account')
    )
    password = models.CharField(
        blank=True, max_length=128, null=True, verbose_name=_('Password')
    )
    password_hash = models.CharField(
        blank=True, max_length=128, null=True, verbose_name=_('Password hash')
    )

    objects = AutoAdminSingletonManager()

    class Meta:
        verbose_name = verbose_name_plural = _('Autoadmin properties')
