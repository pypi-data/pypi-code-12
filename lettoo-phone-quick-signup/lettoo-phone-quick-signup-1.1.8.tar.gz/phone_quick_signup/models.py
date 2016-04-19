from __future__ import unicode_literals

import datetime

from django.db import models
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.crypto import get_random_string

from . import app_settings
from . import signals
from .utils import user_phone, user_phone_verified
from .managers import PhoneNumberManager, PhoneConfirmationManager
from .adapter import get_adapter


@python_2_unicode_compatible
class QuickPhoneNumber(models.Model):
    user = models.ForeignKey(app_settings.USER_MODEL, verbose_name=_('user'))
    phone = models.CharField(unique=app_settings.UNIQUE_PHONE, max_length=254, verbose_name=_('phone number'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    primary = models.BooleanField(verbose_name=_('primary'), default=False)

    objects = PhoneNumberManager()

    class Meta:
        verbose_name = _("quick phone number")
        verbose_name_plural = _("quick phone numbers")
        if not app_settings.UNIQUE_PHONE:
            unique_together = [("user", "phone")]

    def __str__(self):
        return "%s (%s)" % (self.phone, self.user)

    def set_as_primary(self, conditional=False):
        old_primary = QuickPhoneNumber.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        user_phone(self.user, self.phone)
        self.user.save()
        return True

    def send_confirmation(self):
        confirmation = QuickPhoneConfirmation.create(self)
        confirmation.send()
        return confirmation

    def change(self, new_phone, confirm=True):
        """
        Given a new phone number, change self and re-confirm.
        """
        try:
            atomic_transaction = transaction.atomic
        except AttributeError:
            atomic_transaction = transaction.commit_on_success

        with atomic_transaction():
            user_phone(self.user, new_phone)
            user_phone_verified(self.user, False)
            self.user.save()
            self.phone = new_phone
            self.verified = False
            self.primary = True
            self.save()
            if confirm:
                self.send_confirmation()


@python_2_unicode_compatible
class QuickPhoneConfirmation(models.Model):
    phone_number = models.ForeignKey(QuickPhoneNumber, verbose_name=_('phone number'))
    created = models.DateTimeField(verbose_name=_('created'), default=timezone.now)
    sent = models.DateTimeField(verbose_name=_('sent'), null=True)
    key = models.CharField(verbose_name=_('key'), max_length=6, unique=True)

    objects = PhoneConfirmationManager()

    class Meta:
        verbose_name = _("quick phone confirmation")
        verbose_name_plural = _("quick phone confirmations")

    def __str__(self):
        return "confirmation for %s" % self.phone_number

    @classmethod
    def create(cls, phone_number):
        key = get_random_string(6, '0123456789').lower()
        return cls._default_manager.create(phone_number=phone_number, key=key)

    def key_expired(self):
        expiration_date = self.sent + datetime.timedelta(minutes=app_settings.PHONE_CONFIRMATION_EXPIRE_MINUTES)
        return expiration_date <= timezone.now()

    key_expired.boolean = True

    def confirm(self, request, check_verified=True):
        if self.key_expired():
            status = 'invalid'
        elif self.phone_number.verified and check_verified:
            status = 'verified'
        else:
            phone_number = self.phone_number
            get_adapter().confirm_phone(request, phone_number)
            signals.phone_confirmed.send(sender=self.__class__, request=request, phone_number=phone_number)
            status = 'success'
        return self.phone_number, status

    def send(self):
        get_adapter().send_confirmation_sms(key=self.key, to=[self.phone_number.phone])
        self.sent = timezone.now()
        self.save()
        signals.phone_confirmation_sent.send(sender=self.__class__, confirmation=self)
