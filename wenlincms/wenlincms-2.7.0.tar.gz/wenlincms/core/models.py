# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from future.builtins import str
from future.utils import with_metaclass

try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlopen, urlencode
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models
from django.db.models.base import ModelBase
from django.template.defaultfilters import truncatewords_html
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import strip_tags
from django.utils.timesince import timesince
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from wenlincms.core.fields import RichTextField
from wenlincms.core.managers import DisplayableManager
from wenlincms.generic.fields import KeywordsField
from wenlincms.utils.html import TagCloser
from wenlincms.utils.models import base_concrete_model, get_user_model_name
from wenlincms.utils.urls import admin_url, slugify, unique_slug
from wlapps.utils.cache import wl_del_cache

user_model_name = get_user_model_name()


class SiteRelated(models.Model):
    """
    和站点相关的模型，被非池废弃
    """

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Slugged(SiteRelated):
    """
    Abstract model that handles auto-generating slugs. Each slugged
    object is also affiliated with a specific site object.
    """

    title = models.CharField("标题", max_length=200)
    slug = models.CharField("URL", max_length=200, blank=True, null=True,
                            help_text="系统自动根据标题进行计算。")

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        弃用这里的唯一slug算法，改用post_save方法用id计算唯一码
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super(Slugged, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Create a unique slug by passing the result of get_slug() to
        utils.urls.unique_slug, which appends an index if necessary.
        """
        # For custom content types, use the ``Page`` instance for
        # slug lookup.
        concrete_model = base_concrete_model(Slugged, self)
        slug_qs = concrete_model.objects.exclude(id=self.id)
        return unique_slug(slug_qs, "slug", self.get_slug())

    def get_slug(self):
        """
        Allows subclasses to implement their own slug creation logic.
        """
        return slugify(self.title)

    def admin_link(self):
        return "<a href='%s' target='_blank'>%s</a>" % (self.get_absolute_url(), "查看")

    admin_link.allow_tags = True
    admin_link.short_description = ""


class MetaData(models.Model):
    """
    Abstract model that provides meta data for content.
    """

    description = models.TextField("META描述", blank=True, help_text='留空则自动从详细介绍里生成摘要')
    keywords = KeywordsField(verbose_name="标签")

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Set the description field on save.
        """
        if not self.description.strip():
            self.description = self.description_from_content()
        super(MetaData, self).save(*args, **kwargs)

    def meta_title(self):
        """
        Accessor for the optional meta_title field, which returns
        the string version of the instance if not provided.
        """
        return self.title or str(self)

    def description_from_content(self):
        """
        Returns the first block or sentence of the first content-like
        field.
        """
        description = ""
        # Use the first RichTextField, or TextField if none found.
        for field_type in (RichTextField, models.TextField):
            if not description:
                for field in self._meta.fields:
                    if isinstance(field, field_type) and \
                                    field.name != "description":
                        description = getattr(self, field.name)
                        if description:
                            from wenlincms.core.templatetags.wenlincms_tags \
                                import richtext_filters

                            description = richtext_filters(description)
                            break
        # 如果content太短，则用title填充
        description = description.strip() if description else self.title
        # Strip everything after the first block or sentence.
        ends = ("</p>", "<br />", "<br/>", "<br>", "</ul>",
                "\n", ". ", "! ", "? ")
        for end in ends:
            pos = description.lower().find(end)
            if pos > -1:
                description = TagCloser(description[:pos]).html
                break
        description = truncatewords_html(description, 10)
        # 去除html标签
        description = strip_tags(description)
        # 再次检查去除html的tag后的长度
        if not description:
            description = self.title
        elif len(description) < 20:
            description = description + '-' + self.title
        return description.strip()


class TimeStamped(models.Model):
    """
    Provides created and updated timestamps on models.
    """

    class Meta:
        abstract = True

    created = models.DateTimeField('新建时间', null=True, editable=False)
    updated = models.DateTimeField('更新时间', null=True, editable=False)

    def save(self, *args, **kwargs):
        _now = now()
        self.updated = _now
        if not self.id:
            self.created = _now
        super(TimeStamped, self).save(*args, **kwargs)


CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, '下线'),
    (CONTENT_STATUS_PUBLISHED, '上线'),
)

CONTENT_AUDITING_PENDING = 0
CONTENT_AUDITING_ACCEPTING = 1
CONTENT_AUDITING_REJECTED = 2
CONTENT_AUDITING_Init = 3

CONTENT_AUDITING_CHOICES = (
    (CONTENT_AUDITING_PENDING, '待审核'),
    (CONTENT_AUDITING_ACCEPTING, '接受'),
    (CONTENT_AUDITING_REJECTED, '拒绝'),
    (CONTENT_AUDITING_Init, '挂起'),
)


class Displayable(Slugged, MetaData, TimeStamped):
    """
    Abstract model that provides features of a visible page on the
    website such as publishing fields. 
    """
    audit_status = models.SmallIntegerField(_("审阅状态"), db_index=True,
                                            choices=CONTENT_AUDITING_CHOICES, default=CONTENT_AUDITING_PENDING,
                                            help_text=_("需要管理员进行审核，默认是待审核状态"))
    status = models.SmallIntegerField(_("Status"), db_index=True,
                                      choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED,
                                      help_text=_("With Draft chosen, will only be shown for admin users on the site."))
    objects = DisplayableManager()
    search_fields = {"keywords": 10, "title": 5}

    class Meta:
        abstract = True

    def get_admin_url(self):
        return admin_url(self, "change", self.id)

    def publish_date_since(self):
        return timesince(self.created)

    publish_date_since.short_description = _("Published from")

    def get_absolute_url(self):
        """
        Raise an error if called on a subclass without
        ``get_absolute_url`` defined, to ensure all search results
        contains a URL.
        """
        name = self.__class__.__name__
        raise NotImplementedError("The model %s does not have "
                                  "get_absolute_url defined" % name)

    def save(self, *args, **kwargs):
        # 下面更新对应的详情页的缓存
        # 缓存主动更新相关库
        wl_del_cache(self.get_absolute_url())
        super(Displayable, self).save(*args, **kwargs)

    def _get_next_or_previous_by_publish_date(self, is_next, **kwargs):
        """
        Retrieves next or previous object by publish date. We implement
        our own version instead of Django's so we can hook into the
        published manager and concrete subclasses.
        """
        arg = "created__gt" if is_next else "created__lt"
        order = "created" if is_next else "-created"
        lookup = {arg: self.created}
        concrete_model = base_concrete_model(Displayable, self)
        try:
            queryset = concrete_model.objects.published
        except AttributeError:
            queryset = concrete_model.objects.all
        try:
            return queryset(**kwargs).filter(**lookup).order_by(order)[0]
        except IndexError:
            pass

    def get_next_by_publish_date(self, **kwargs):
        """
        Retrieves next object by publish date.
        """
        return self._get_next_or_previous_by_publish_date(True, **kwargs)

    def get_previous_by_publish_date(self, **kwargs):
        """
        Retrieves previous object by publish date.
        """
        return self._get_next_or_previous_by_publish_date(False, **kwargs)


class RichText(models.Model):
    """
    Provides a Rich Text field for managing general content and making
    it searchable.
    """

    content = RichTextField(_("Content"))

    search_fields = ("content",)

    class Meta:
        abstract = True


class OrderableBase(ModelBase):
    """
    Checks for ``order_with_respect_to`` on the model's inner ``Meta``
    class and if found, copies it to a custom attribute and deletes it
    since it will cause errors when used with ``ForeignKey("self")``.
    Also creates the ``ordering`` attribute on the ``Meta`` class if
    not yet provided.
    """

    def __new__(cls, name, bases, attrs):
        if "Meta" not in attrs:
            class Meta:
                pass

            attrs["Meta"] = Meta
        if hasattr(attrs["Meta"], "order_with_respect_to"):
            order_field = attrs["Meta"].order_with_respect_to
            attrs["order_with_respect_to"] = order_field
            del attrs["Meta"].order_with_respect_to
        if not hasattr(attrs["Meta"], "ordering"):
            setattr(attrs["Meta"], "ordering", ("_order",))
        return super(OrderableBase, cls).__new__(cls, name, bases, attrs)


class Orderable(with_metaclass(OrderableBase, models.Model)):
    """
    Abstract model that provides a custom ordering integer field
    similar to using Meta's ``order_with_respect_to``, since to
    date (Django 1.2) this doesn't work with ``ForeignKey("self")``,
    or with Generic Relations. We may also want this feature for
    models that aren't ordered with respect to a particular field.
    """

    _order = models.IntegerField(_("Order"), null=True)

    class Meta:
        abstract = True

    def with_respect_to(self):
        """
        Returns a dict to use as a filter for ordering operations
        containing the original ``Meta.order_with_respect_to`` value
        if provided. If the field is a Generic Relation, the dict
        returned contains names and values for looking up the
        relation's ``ct_field`` and ``fk_field`` attributes.
        """
        try:
            name = self.order_with_respect_to
            value = getattr(self, name)
        except AttributeError:
            # No ``order_with_respect_to`` specified on the model.
            return {}
        # Support for generic relations.
        field = getattr(self.__class__, name)
        if isinstance(field, GenericForeignKey):
            names = (field.ct_field, field.fk_field)
            return dict([(n, getattr(self, n)) for n in names])
        return {name: value}

    def save(self, *args, **kwargs):
        """
        Set the initial ordering value.
        """
        if self._order is None:
            lookup = self.with_respect_to()
            lookup["_order__isnull"] = False
            concrete_model = base_concrete_model(Orderable, self)
            self._order = concrete_model.objects.filter(**lookup).count()
        super(Orderable, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Update the ordering values for siblings.
        """
        lookup = self.with_respect_to()
        lookup["_order__gte"] = self._order
        concrete_model = base_concrete_model(Orderable, self)
        after = concrete_model.objects.filter(**lookup)
        after.update(_order=models.F("_order") - 1)
        super(Orderable, self).delete(*args, **kwargs)

    def _get_next_or_previous_by_order(self, is_next, **kwargs):
        """
        Retrieves next or previous object by order. We implement our
        own version instead of Django's so we can hook into the
        published manager, concrete subclasses and our custom
        ``with_respect_to`` method.
        """
        lookup = self.with_respect_to()
        lookup["_order"] = self._order + (1 if is_next else -1)
        concrete_model = base_concrete_model(Orderable, self)
        try:
            queryset = concrete_model.objects.published
        except AttributeError:
            queryset = concrete_model.objects.filter
        try:
            return queryset(**kwargs).get(**lookup)
        except concrete_model.DoesNotExist:
            pass

    def get_next_by_order(self, **kwargs):
        """
        Retrieves next object by order.
        """
        return self._get_next_or_previous_by_order(True, **kwargs)

    def get_previous_by_order(self, **kwargs):
        """
        Retrieves previous object by order.
        """
        return self._get_next_or_previous_by_order(False, **kwargs)


class Ownable(models.Model):
    """
    Abstract model that provides ownership of an object for a user.
    """

    user = models.ForeignKey(user_model_name, verbose_name=_("Author"),
                             related_name="%(class)ss")

    class Meta:
        abstract = True

    def is_editable(self, request):
        """
        Restrict in-line editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or request.user.id == self.user_id
