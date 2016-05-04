from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class AbstractAuthSchBase(AbstractBaseUser, PermissionsMixin):
    auth_sch_internal_id = models.CharField(max_length=100, unique=True, blank=True)
    access_token = models.CharField(max_length=100, unique=True, blank=True)
    refresh_token = models.CharField(max_length=100, unique=True, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    USERNAME_FIELD = 'auth_sch_internal_id'

    class Meta:
        abstract = True

    def get_short_name(self):
        return self.auth_sch_internal_id

    def get_full_name(self):
        return self.auth_sch_internal_id
