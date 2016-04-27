""" Models. """

from django.conf import settings
from django.db import models


# Create your models here.
class GroupProfile(models.Model):
    """
    Extension to Group model.
    """
    group = models.OneToOneField('auth.Group', unique=True)

    # The segment of the URI after the site DOI URI that defines this domain
    # within site DOI name space
    doi_suffix = models.CharField('DOI suffix - doi:' + settings.DOI_PREFIX
                                  + '/', max_length=100)

    def __unicode__(self):  # __unicode__ on Python 2
        return self.doi_suffix
