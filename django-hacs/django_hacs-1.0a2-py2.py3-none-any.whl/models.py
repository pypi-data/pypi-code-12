from __future__ import unicode_literals

from django.db import models
from django.apps import apps
from django.utils import six
from django.utils import timezone
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.fields import GenericForeignKey


from .fields import DictField
from .fields import SequenceField

if not apps.is_installed('django.contrib.admin'):
    # Fallback LogEntry Model, if admin app not installed
    from django.contrib.admin.models import LogEntry as django_LogEntry

    class LogEntry(django_LogEntry):
        pass

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class RoutingTableManager(models.Manager):
    """"""
    use_in_migrations = True

    def get_by_natural_key(self, route_name):
        """
        :param route_name:
        :return:
        """
        return self.get(route_name=route_name)


@python_2_unicode_compatible
class RoutingTable(models.Model):
    """
    JSON Field Permitted Format/Python Data pattern
    -----------------------------------------------
    urls: [{'prefix': None, 'url_module': None, namespace=None, children: []}]
    OR [{'prefix': None, 'url_module': (module, app_name), namespace=None, children: []}]

    handlers: {'handler400': None, 'handler403': None, 'handler404': None, 'handler500': None}
    """
    route_name = models.SlugField(_('route name'),  null=False, blank=False, unique=True, db_index=True, max_length=127)
    description = models.TextField(_('description'), null=True, blank=True)
    urls = SequenceField(_('URLs'), null=False, blank=False, validators=[])
    handlers = DictField(_('Handlers'), null=True, blank=True, default='', validators=[])
    generated_module = models.TextField(_('Generated Module'), null=True, blank=True, default=None)
    is_active = models.BooleanField(_('Is Active'), null=False, blank=True, default=True)
    is_deleted = models.BooleanField(_('Soft Delete'), null=False, blank=True, default=False)
    created_on = models.DateTimeField(_('Created On'), blank=True, default=timezone.now)
    updated_on = models.DateTimeField(_('Last updated'), null=True, blank=True)

    objects = RoutingTableManager()

    class Meta:
        db_table = 'hacl_routing_table'
        verbose_name = _('routing table')
        verbose_name_plural = _('routes table')

    def natural_key(self):
        """
        :return:
        """
        return (self.route_name, )

    def __str__(self):
        """
        """
        return self.route_name


class SiteRoutingTableManager(models.Manager):
    """ """
    use_in_migrations = True

    def get_by_natural_key(self, site_natural_key):
        """
        :param site_natural_key:
        :return:
        """
        if isinstance(site_natural_key, six.string_types):
            site_natural_key = (site_natural_key,)

        try:
            if not isinstance(site_natural_key, (list, tuple,)):
                snk = (site_natural_key, )
            else:
                snk = site_natural_key
            site = Site.objects.db_manager(self.db).get_by_natural_key(*snk)
        except AttributeError:
            if isinstance(site_natural_key, six.integer_types):
                site = Site.objects.db_manager(self.db).get(pk=site_natural_key)
            else:
                raise

        return self.get(site=site)


class SiteRoutingTable(models.Model):

    """
    """
    route = models.ForeignKey(RoutingTable,
                              on_delete=models.CASCADE,
                              db_column='route_id',
                              db_constraint=False,
                              related_name='hacs_route_sites')
    site = models.OneToOneField(Site,
                             on_delete=models.CASCADE,
                             unique=True,
                             null=False,
                             blank=False,
                             related_name='hacs_site_routes')
    is_active = models.BooleanField(_('Is Active'), null=False, blank=True, default=True)
    created_on = models.DateTimeField(_('Created On'), blank=True, default=timezone.now)
    updated_on = models.DateTimeField(_('Last updated'), null=True, blank=True)

    objects = SiteRoutingTableManager()

    class Meta:
        db_table = 'hacs_sites_routing_table'
        verbose_name = _('site routing table')
        verbose_name_plural = _('sites routing table')

    def natural_key(self):
        """
        :return:
        """
        try:
            site_natural_key = self.site.natural_key()
        except AttributeError:
            # Right now `natural_key` is not implemented by django, but would be good if they do
            site_natural_key = self.site.pk

        return (site_natural_key, )
    natural_key.dependencies = ["hacs.RoutingTable", "sites.Site"]


class ContentTypeRoutingTableManager(models.Manager):
    """ """
    use_in_migrations = True

    def get_by_natural_key(self, site_nk, content_type_nk, object_id):
        """
        :param site_nk:
        :param content_type_nk
        :param object_id
        :return:
        """
        if isinstance(site_nk, six.string_types):
            site_nk = (site_nk,)

        if isinstance(content_type_nk, six.string_types):
            content_type_nk = (content_type_nk,)

        try:
            if not isinstance(site_nk, (list, tuple)):
                snk = (site_nk, )
            else:
                snk = site_nk
            site = Site.objects.db_manager(self.db).get_by_natural_key(*snk)
        except AttributeError:
            if isinstance(site_nk, six.integer_types):
                site = Site.objects.db_manager(self.db).get(pk=site_nk)
            else:
                raise

        return self.get(
            site=site,
            content_type=ContentType.objects.db_manager(self.db).get_by_natural_key(*content_type_nk),
            object_id=object_id
        )


class ContentTypeRoutingTable(models.Model):

    """
    """
    route = models.ForeignKey(RoutingTable,
                              on_delete=models.CASCADE,
                              db_column='route_id',
                              db_constraint=False,
                              related_name='hacs_route_contenttypes',
                              validators=[],
                              )
    site = models.ForeignKey(Site,
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name='hacs_site_contenttypes_at_routing_table'
                             )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, validators=[])
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    is_active = models.BooleanField(_('Is Active'), null=False, blank=True, default=True)
    created_on = models.DateTimeField(_('Created On'),  blank=True, default=timezone.now)
    updated_on = models.DateTimeField(_('Last updated'), null=True, blank=True)

    objects = ContentTypeRoutingTableManager()

    class Meta:
        db_table = 'hacs_ct_routing_table'
        verbose_name = _('content type routing table')
        verbose_name_plural = _('content types routing table')
        unique_together = (("site", "content_type", "object_id"),)

    def natural_key(self):
        """
        :return:
        """
        try:
            site_natural_key = self.site.natural_key()
        except AttributeError:
            # Right now `natural_key` is not implemented by django, but would be good if they do
            site_natural_key = self.site.pk

        return (site_natural_key, self.content_type.natural_key(), self.object_id, )

    natural_key.dependencies = ["hacs.RoutingTable", "sites.Site", "contenttypes.ContentType"]
