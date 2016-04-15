from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.db.models import Q

from . import app_settings


class PhoneNumberManager(models.Manager):
    def add_phone(self, user, phone, confirm=False):
        try:
            phone_number = self.get(user=user, phone__iexact=phone)
        except self.model.DoesNotExist:
            phone_number = self.create(user=user, phone=phone)
            if confirm:
                phone_number.send_confirmation()
        return phone_number

    def get_primary(self, user):
        try:
            return self.get(user=user, primary=True)
        except self.model.DoesNotExist:
            return None

    def fill_cache_for_user(self, user, numbers):
        """
        In a multi-db setup, inserting records and re-reading them later
        on may result in not being able to find newly inserted
        records. Therefore, we maintain a cache for the user so that
        we can avoid database access when we need to re-read..
        """
        user._phone_number_cache = numbers

    def get_for_user(self, user, phone):
        cache_key = '_phone_number_cache'
        numbers = getattr(user, cache_key, None)
        if numbers is None:
            ret = self.get(user=user, phone__iexact=phone)
            ret.user = user
            return ret
        else:
            for number in numbers:
                if number.phone.lower() == phone.lower():
                    return number
            raise self.model.DoesNotExist()


class PhoneConfirmationManager(models.Manager):
    def all_expired(self):
        return self.filter(self.expired_q())

    def all_valid(self):
        return self.exclude(self.expired_q())

    def expired_q(self):
        sent_threshold = timezone.now() - timedelta(minutes=app_settings.PHONE_CONFIRMATION_EXPIRE_MINUTES)
        return Q(sent__lt=sent_threshold)

    def delete_expired_confirmations(self):
        self.all_expired().delete()
