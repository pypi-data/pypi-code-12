from __future__ import unicode_literals
import hashlib
import random
import re

from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import six
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from sendsms.message import SmsMessage
import base32_crockford

from .settings import *
import common.models


class UserManager(object):
    """
    Should be used as a mixin with your custom UserManager class
    """

    def _create_user(self, email, password, is_active, is_staff, is_superuser, **extra_fields):

        user = self.model(email=email, is_staff=is_staff, is_active=is_active,
                          is_superuser=is_superuser, **extra_fields)
        user.set_password(password)

        mobile_phone = extra_fields.get('mobile_phone')

        if not is_active:
            if email:
                EmailRegistration.objects.create_inactive_user(user)
            if SMS_ENABLED and mobile_phone:
                SMSRegistration.objects.create_inactive_user(user)
        else:
            user.save()
            if email:
                EmailRegistration.objects.create_registration(
                    user, verified=True, send_message=not is_superuser
                )
            if SMS_ENABLED and mobile_phone:
                SMSRegistration.objects.create_registration(user, verified=True)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, False, **extra_fields)


class RegistrationManager(models.Manager):

    @property
    def code_re(self):
        raise NotImplementedError('Please implement the code_re property')

    @staticmethod
    def _verify_user(user):
        raise NotImplementedError('Please implement the _verify_user property')

    def verify(self, verification_code):
        if self.code_re.search(verification_code):
            try:
                registration = self.get(verification_code=verification_code)
            except self.model.DoesNotExist:
                return False
            if not registration.expired():
                self._verify_user(registration)
                # Delete other registrations that are verified for this User
                self.filter(user=registration.user, verification_code=self.model.VERIFIED).delete()
                registration.verification_code = self.model.VERIFIED
                registration.save()
                return registration
        return False

    def create_verified_registration(self, user):
        raise NotImplementedError('Please implement the create_verified_registration method')

    def create_inactive_user(self, new_user=None, send_message=True, request=None, **user_info):

        if new_user is None:
            password = user_info.pop('password')
            new_user = get_user_model()(**user_info)
            new_user.set_password(password)
        new_user.is_active = False
        new_user.save()

        self.create_registration(new_user, send_message=send_message)

        return new_user

    @staticmethod
    def _generate_code(user):
        raise NotImplementedError("Please implement the _generate_code method")

    def create_registration(self, user, verified=False):
        raise NotImplementedError("Please implement the create_registration method")

    def delete_expired(self):
        for registration in self.all():
            try:
                if registration.expired():
                    user = registration.user
                    if not user.is_active:
                        user.delete()
                    registration.delete()
            except get_user_model().DoesNotExist:
                registration.delete()


class EmailRegistrationManager(RegistrationManager):

    code_re = re.compile('^[A-F0-9]{40}$')

    @staticmethod
    def _generate_code(user):
        salt = hashlib.sha1(six.text_type(random.random()).encode('ascii')).hexdigest()[:5]
        salt = salt.encode('ascii')
        user_pk = str(user.pk)
        if isinstance(user_pk, six.text_type):
            user_pk = user_pk.encode('utf-8')
        return hashlib.sha1(salt+user_pk).hexdigest()

    @staticmethod
    def _verify_user(registration):
        registration.user.is_active = True
        registration.user.email_verified_on = timezone.now()
        registration.user.email = registration.email
        registration.user.save()
        return registration

    def create_registration(self, user, verified=False, send_message=True):
        try:
            registration = self.get(email=user.email)
        except EmailRegistration.DoesNotExist:
            verification_code = self.model.VERIFIED if verified else self._generate_code(user)
            registration = self.create(user=user, verification_code=verification_code, email=user.email)

        if send_message and registration.verification_code != self.model.VERIFIED:
            registration.send_message()

        return registration


class SMSRegistrationManager(RegistrationManager):

    code_re = re.compile('^[' + base32_crockford.symbols + ']{6}$')

    @staticmethod
    def _generate_code(user):
        return base32_crockford.encode(random.randrange(33554432, 1073741823))

    @staticmethod
    def _verify_user(registration):
        registration.user.is_active = True
        registration.user.mobile_phone_verified_on = timezone.now()
        registration.user.mobile_phone = registration.mobile_phone
        registration.user.save()
        return registration

    def create_registration(self, user, verified=False, send_message=True):
        try:
            registration = self.get(mobile_phone=user.mobile_phone)
        except SMSRegistration.DoesNotExist:
            verification_code = self.model.VERIFIED if verified else self._generate_code(user)
            registration = self.create(user=user, verification_code=verification_code, mobile_phone=user.mobile_phone)

        if send_message and registration.verification_code != self.model.VERIFIED:
            registration.send_message()

        return registration


class Registration(common.models.DateTimeModelMixin):

    VERIFIED = None

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    verification_code = models.CharField(_('Verification Code'), max_length=255, null=True)

    class Meta:
        abstract = True

    @property
    def service(self):
        raise NotImplementedError("Please implement the service property")

    @property
    def verification_timedelta(self):
        return globals()['{}_VERIFICATION_TIMEDELTA'.format(self.service)]

    def expired(self):
        expiration = self.verification_timedelta
        return self.verification_code == self.VERIFIED or (self.created_at + expiration <= timezone.now())
    expired.boolean = True


class EmailRegistration(Registration):

    service = 'EMAIL'

    email = models.EmailField(_('Email Address'), unique=True, db_index=True)

    objects = EmailRegistrationManager()

    class Meta:
        verbose_name = _('Email Registration')
        verbose_name_plural = _('Email Registrations')

    def __unicode__(self):
        return "Email registration for %s" % self.user

    def send_message(self, request=None):
        # TODO This should be backgrounded to a task queue
        ctx_dict = {}
        if request is not None:
            ctx_dict = RequestContext(request, ctx_dict)
        # update ctx_dict after RequestContext is created
        # because template context processors
        # can overwrite some of the values like user
        # if django.contrib.auth.context_processors.auth is used
        ctx_dict.update({
            'site_host': settings.SITE_HOST,
            'user': self.user,
            'verification_code': self.verification_code,
            'expiration_days': EMAIL_VERIFICATION_TIMEDELTA.days
        })
        subject = getattr(settings, 'EMAIL_SUBJECT_PREFIX', '') + render_to_string('verification_email_subject.txt',
                                                                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        from_email = settings.DEFAULT_FROM_EMAIL
        message_txt = render_to_string('verification_email.txt', ctx_dict)

        email_message = EmailMultiAlternatives(subject, message_txt, from_email, [self.user.email],
                                               headers={'X-Verification-Code': self.verification_code})
        message_html = render_to_string('verification_email.html', ctx_dict)

        email_message.attach_alternative(message_html, 'text/html')
        email_message.send()


class SMSRegistration(Registration):
    objects = SMSRegistrationManager()

    service = 'SMS'

    mobile_phone = models.CharField(_('Mobile Phone'), unique=True, db_index=True, max_length=12)

    @property
    def verification_code_formatted(self):
        if self.verification_code:
            return '-'.join(re.findall('.{1,3}', self.verification_code))

    class Meta:
        verbose_name = _('SMS Registration')
        verbose_name_plural = _('SMS Registrations')

    def __unicode__(self):
        return "SMS registration for %s" % self.user

    def send_message(self):
        # TODO This should be sent to task queue

        ctx_dict = {
            'site_host': settings.SITE_HOST,
            'site_name_short': settings.SITE_NAME_SHORT,
            'verification_code': self.verification_code_formatted,
            'expiration_minutes': SMS_VERIFICATION_TIMEDELTA.seconds / 60,
        }
        sms_body = render_to_string('verification_sms.txt', ctx_dict)
        SmsMessage(body=sms_body, to=[self.user.mobile_phone]).send()
