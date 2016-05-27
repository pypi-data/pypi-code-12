""" django_sites_extensions module signals """
from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.contrib.redirects.models import Redirect


@receiver(post_delete, sender=Redirect)
@receiver(post_save, sender=Redirect)
def clear_redirect_cache(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Clears the Redirect cache
    """
    cache.delete(settings.REDIRECT_CACHE_KEY)
