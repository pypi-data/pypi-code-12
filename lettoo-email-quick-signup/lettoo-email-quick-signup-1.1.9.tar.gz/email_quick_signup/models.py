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
from .utils import user_email, user_email_verified
from .managers import EmailAddressManager, EmailConfirmationManager
from .adapter import get_adapter


@python_2_unicode_compatible
class QuickEmailAddress(models.Model):
    user = models.ForeignKey(app_settings.USER_MODEL, verbose_name=_('user'))
    email = models.EmailField(unique=app_settings.UNIQUE_EMAIL, max_length=254, verbose_name=_('e-mail address'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)
    primary = models.BooleanField(verbose_name=_('primary'), default=False)

    objects = EmailAddressManager()

    class Meta:
        verbose_name = _("quick email address")
        verbose_name_plural = _("quick email addresses")
        if not app_settings.UNIQUE_EMAIL:
            unique_together = [("user", "email")]

    def __str__(self):
        return "%s (%s)" % (self.email, self.user)

    def set_as_primary(self, conditional=False):
        old_primary = QuickEmailAddress.objects.get_primary(self.user)
        if old_primary:
            if conditional:
                return False
            old_primary.primary = False
            old_primary.save()
        self.primary = True
        self.save()
        user_email(self.user, self.email)
        self.user.save()
        return True

    def send_confirmation(self, request=None, signup=False):
        confirmation = QuickEmailConfirmation.create(self)
        confirmation.send(request, signup=signup)
        return confirmation

    def change(self, request, new_email, confirm=True):
        """
        Given a new email address, change self and re-confirm.
        """
        try:
            atomic_transaction = transaction.atomic
        except AttributeError:
            atomic_transaction = transaction.commit_on_success

        with atomic_transaction():
            user_email(self.user, new_email)
            user_email_verified(self.user, False)
            self.user.save()
            self.email = new_email
            self.verified = False
            self.primary = True
            self.save()
            if confirm:
                self.send_confirmation(request)


@python_2_unicode_compatible
class QuickEmailConfirmation(models.Model):
    email_address = models.ForeignKey(QuickEmailAddress, verbose_name=_('e-mail address'))
    created = models.DateTimeField(verbose_name=_('created'), default=timezone.now)
    sent = models.DateTimeField(verbose_name=_('sent'), null=True)
    key = models.CharField(verbose_name=_('key'), max_length=6, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        verbose_name = _("quick email confirmation")
        verbose_name_plural = _("quick email confirmations")

    def __str__(self):
        return "confirmation for %s" % self.email_address

    @classmethod
    def create(cls, email_address):
        key = get_random_string(6, '0123456789').lower()
        return cls._default_manager.create(email_address=email_address, key=key)

    def key_expired(self):
        expiration_date = self.sent \
                          + datetime.timedelta(days=app_settings
                                               .EMAIL_CONFIRMATION_EXPIRE_DAYS)
        return expiration_date <= timezone.now()

    key_expired.boolean = True

    def confirm(self, request, check_verified=True):
        if self.key_expired():
            status = 'invalid'
        elif self.email_address.verified and check_verified:
            status = 'verified'
        else:
            email_address = self.email_address
            get_adapter().confirm_email(request, email_address)
            signals.email_confirmed.send(sender=self.__class__,
                                         request=request,
                                         email_address=email_address)
            status = 'success'
        return self.email_address, status

    def send(self, request=None, signup=False):
        get_adapter().send_confirmation_mail(request, self, signup)
        self.sent = timezone.now()
        self.save()
        signals.email_confirmation_sent.send(sender=self.__class__, confirmation=self)
