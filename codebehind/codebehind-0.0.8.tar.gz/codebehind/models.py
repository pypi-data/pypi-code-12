import uuid
import os
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
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
	key = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.OneToOneField(User, related_name='secret')
	is_verified = models.BooleanField(default=False)

	def __str__(self):
		return "%s" % self.key

	def __unicode__(self):
		return '%s' % self.key