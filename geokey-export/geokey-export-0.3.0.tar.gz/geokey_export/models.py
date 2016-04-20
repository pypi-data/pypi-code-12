from django.dispatch import receiver
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis

from geokey.projects.models import Project


class Export(models.Model):
    """
    Stores a single export.
    """
    name = models.CharField(max_length=100)
    project = models.ForeignKey('projects.Project')
    category = models.ForeignKey('categories.Category', null=True, blank=True)
    isoneoff = models.BooleanField(default=False)
    expiration = models.DateTimeField(null=True)
    urlhash = models.CharField(max_length=40)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)
    bounding_box = gis.PolygonField(null=True, geography=True)

    def is_expired(self):
        if self.expiration:
            return self.expiration < timezone.now()

        return False

    def expire(self):
        self.expiration = timezone.now()
        self.save()


@receiver(models.signals.post_save, sender=Project)
def post_save_project(sender, instance, **kwargs):
    """
    Receiver that is called after a project is saved. It is used to remove the
    export when project is deleted.
    """
    if instance.status == 'deleted':
        Export.objects.filter(project=instance).delete()
