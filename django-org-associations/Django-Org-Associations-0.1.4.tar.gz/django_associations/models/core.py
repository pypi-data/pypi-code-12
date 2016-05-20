"""
These are the models at the core of the functionality.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from . import abstracts

# pylint: disable=no-member

class Organisation(abstracts.Abstract):
    "Organisations"
    label = models.CharField(max_length=128, unique=True)


class Member(abstracts.Abstract):
    "Defines Membership of organisations."
    user = models.ForeignKey(User, related_name='association_member')
    organisation = models.ForeignKey(Organisation, related_name='member',
                                     blank=True)
    uid_verifier = models.UUIDField(unique=True, default=uuid.uuid4, null=True)
    has_accepted = models.BooleanField(default=False)
    org_managers = models.BooleanField(default=False)
    hrm_managers = models.BooleanField(default=False)

    def __str__(self):
        return str(self.organisation) + ' : ' + str(self.user)


class Association(abstracts.Abstract):
    "Associations"
    _txt_related = 'association_organisation'
    organisation = models.ForeignKey(Organisation, related_name=_txt_related)

    _txt_related = 'association_associations'
    associations = models.ManyToManyField(Organisation, blank=True,
                                          related_name=_txt_related)

    def __str__(self):
        return str(self.organisation) + ' : '  +  str(self.associations.all())
