# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from tagging.fields import TagField

from .managers import ContentManager
from .utils import dum_request, parse_cms_template
from .validators import validate_and_get_template, validate_url_path


class Category(models.Model):
    """Category model."""
    title = models.CharField(_('title'), max_length=100,
                             unique=True, db_index=True)
    description = models.TextField(_('description'))

    class Meta(object):
        verbose_name_plural = _('categories')
        ordering = ('title',)

    def __unicode__(self):
        return self.title

    def delete(self, *args, **kwargs):
        assert self.pk is not 1, (
            'Will not delete {} category. Shit breaks if it happens'.format(
                self.title
            )
        )
        super(Category, self).delete(*args, **kwargs)


def cms_authors():
    User = get_user_model()
    users = User.objects.filter(
        Q(user_permissions__codename='change_content',
          user_permissions__content_type__app_label='cfblog') |
        Q(groups__permissions__codename='change_content',
          groups__permissions__content_type__app_label='cfblog') |
        Q(is_superuser=True)
    ).distinct()

    return {'pk__in': users.values('pk')}


class Content(models.Model):
    DRAFT = 1
    PUBLIC = 2
    STATUS_CHOICES = (
        (DRAFT, _('Draft')),
        (PUBLIC, _('Public')),
    )
    url = models.CharField(_('url path'), max_length=255, db_index=True,
                           unique=True, validators=[validate_url_path])
    template = models.CharField(verbose_name=_('template'), max_length=255,
                                validators=[validate_and_get_template])
    status = models.IntegerField(
        _('status'), choices=STATUS_CHOICES, default=DRAFT
    )
    publish = models.DateTimeField(_('publish'), default=timezone.now)
    title = models.CharField(_('title'), max_length=200)
    category = models.ForeignKey('Category')
    tags = TagField()
    tease = models.TextField(
        _('tease'), blank=True,
        help_text=_('Concise text suggested. Does not appear in RSS feed.')
    )
    notes_todos = models.TextField(_('Notes and Todos'), blank=True)
    auth_data = JSONField(
        verbose_name=_('author data'), default={}, blank=True,
        help_text=_("Don't edit this unless you know what this means")
    )
    public_data = JSONField(
        verbose_name=_('public data'), default={}, blank=True,
        help_text=_("Don't edit this unless you know what this means")
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               limit_choices_to=cms_authors)
    created_on = models.DateTimeField(_('created on'), auto_now_add=True)
    modified_on = models.DateTimeField(_('modified on'), auto_now=True)
    objects = ContentManager()

    class Meta(object):
        ordering = ('-publish',)
        get_latest_by = 'publish'
        permissions = (('can_publish', "Can Publish Posts"),)

    @property
    def is_public(self):
        return self.status == self.PUBLIC

    def publish_cms_content(self):
        self.public_data = self.auth_data
        self.status = self.PUBLIC
        self.save()

    def __unicode__(self):
        return self.title

    def get_previous_post(self):
        return self.get_previous_by_publish(
            Q(status__gte=self.PUBLIC), ~Q(category_id=1)
        )

    def get_next_post(self):
        return self.get_next_by_publish(
            Q(status__gte=self.PUBLIC), ~Q(category_id=1)
        )

    def get_absolute_url(self):
        return self.url

    def get_public_html(self, request=dum_request,
                        template_context=None, using=None):
        # This is only recommended for internal usages
        # where you want to extract the html content
        # without publishing the page
        template_context = template_context or {}
        template_context['cms_content'] = self
        template = validate_and_get_template(self.template, using=using)
        content = template.render(context=template_context, request=request)
        return parse_cms_template(
            html=content, cms_context=self.public_data, public=True,
            request=request, template_context=template_context
        )
