# -*- coding: utf-8 -*-
import warnings
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now as tz_now
from django.core.files.storage import FileSystemStorage

from taggit.managers import TaggableManager

from bazar.utils.filefield import content_file_name

def get_file_uploadto(x, y):
    """
    Callabe to return uploadto path for a file
    """
    return content_file_name('bazar/attachments/%Y/%m/%d', x, y)

def enforce_choices_translation(choices):
    """
    For unknown reasons, Django does not apply i18n machinery on choices labels coming
    from settings, so enforce them there (and also in some other methods, see
    templatetags)
    """
    choices = list(choices)
    return tuple( [(k, _(v)) for k,v in choices] )

# Check for django-sendfile availibility
try:
    from sendfile import sendfile
except ImportError:
    warnings.warn("Bazar note attachment should be private but you don't have installed 'django-sendfile' so for now your attachment will be public for everyone. Install it to avoid this warning.", UserWarning)
    ATTACHMENTS_WITH_SENDFILE = False
    ATTACHMENT_FS_STORAGE = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
else:
    ATTACHMENTS_WITH_SENDFILE = True
    ATTACHMENT_FS_STORAGE = FileSystemStorage(location=settings.SENDFILE_ROOT, base_url=settings.SENDFILE_URL)


class Entity(models.Model):
    """
    Entity

    Most of informations for notes are related to an entity, so it's best to
    have them to improve data structures.
    """
    created = models.DateTimeField(_("created"), editable=False, null=True, blank=True)
    modified = models.DateTimeField(_("modified"), editable=False, null=True, blank=True)

    kind = models.CharField(_('kind'), choices=enforce_choices_translation(settings.ENTITY_KINDS), default=settings.DEFAULT_ENTITY_KIND, max_length=40, blank=False)

    name = models.CharField(_("name"), blank=False, max_length=255, unique=True)

    adress = models.TextField(_('full adress'), blank=True)
    phone = models.CharField(_('phone'), max_length=15, blank=True)
    fax = models.CharField(_('fax'), max_length=15, blank=True)
    town = models.CharField(_('town'), max_length=75, blank=True)
    zipcode = models.CharField(_('zipcode'), max_length=6, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('bazar:entity-detail', [self.kind, self.id])

    def save(self, *args, **kwargs):
        """
        Fill 'created' and 'modified' attributes on first create
        """
        if self.created is None:
            self.created = tz_now()

        if self.modified is None:
            self.modified = self.created

        super(Entity, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")


class Note(models.Model):
    """
    Note
    """
    created = models.DateTimeField(_("created"), editable=False, null=True, blank=True)
    modified = models.DateTimeField(_("modified"), editable=False, null=True, blank=True)

    author = models.ForeignKey(User, verbose_name=_("author"))#, editable=False, blank=False)
    entity = models.ForeignKey(Entity, verbose_name=_("entity"), null=True, blank=True)

    title = models.CharField(_("title"), max_length=150)
    content = models.TextField(_('content'), blank=True)
    file = models.FileField(_('file'), upload_to=get_file_uploadto, storage=ATTACHMENT_FS_STORAGE, max_length=255, null=True, blank=True)

    tags = TaggableManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('bazar:note-details', [self.id])

    def save(self, *args, **kwargs):
        """
        Fill 'created' and 'modified' attributes on first create
        """
        if self.created is None:
            self.created = tz_now()

        if self.modified is None:
            self.modified = self.created

        super(Note, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
