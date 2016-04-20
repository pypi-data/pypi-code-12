from django.db import models


class CartoDbProject(models.Model):
    enabled = models.BooleanField(default=False)
    project = models.OneToOneField(
        'projects.Project',
        primary_key=True,
        related_name='cartodb'
    )

    objects = models.Manager()
