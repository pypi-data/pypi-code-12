import binascii
import os
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_secret(sender, instance=None, created=False, **kwargs):
	if created:
		key = UserSecret.objects.create(user=instance)
		if settings.DEBUG:
			print key


class TimeStampedModel(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True


class UserSecret(TimeStampedModel):
	key = models.CharField(max_length=40, primary_key=True)
	user = models.OneToOneField(User, related_name='secret')
	is_verified = models.BooleanField(default=False)
	verification_code = models.CharField(max_length=40)

	def save(self, *args, **kwargs):
		if not self.key:
			self.key = self.generate_key()
			self.verification_code = self.generate_key()
		return super(UserSecret, self).save(*args, **kwargs)

	def generate_key(self):
		return "%s"  % binascii.hexlify(os.urandom(20)).decode()

	def __str__(self):
		return "%s" % self.key

	def __unicode__(self):
		return '%s' % self.key