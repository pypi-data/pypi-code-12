from __future__ import print_function
import traceback

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor, \
    ForeignKey
from django.db.models.manager import Manager
from django.db.models.fields import FieldDoesNotExist

try:
    from django.utils.text import slugify
except ImportError:
    from django.template.defaultfilters import slugify


class QueryReport(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    base_object = models.ForeignKey(ContentType)
    order_by = models.CharField(max_length=255, blank=True)
    template_name = models.CharField(max_length=255, blank=True)
    distinct = models.BooleanField(blank=True, default=False)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:30]
        super(QueryReport, self).save(**kwargs)

    def build_queryset(self, variables={}, link_fks=True):
        qs = self.base_object.model_class().objects.all()

        if self.distinct:
            qs = qs.distinct()

        for filter in self.filters.all():
            value = filter.value.strip()
            if value.startswith("@"):
                value = variables.get(value.lstrip("@"))
            else:
                if value.lower() == "false":
                    value = False
                elif value.lower() == "true":
                    value = True
                elif "," in value:
                    value = value.split(",")

            kwarg = {filter.path: value}

            if filter.exclude:
                qs = qs.exclude(**kwarg)
            else:
                qs = qs.filter(**kwarg)

        # all aggregates
        if self.columns.exclude(aggregation="").count() == self.columns.count():
            headers = []
            kwargs = {}
            for column in self.columns.exclude(aggregation=""):
                kwargs[column.name] = {
                        "sum": models.Sum,
                        "count": models.Count,
                        "min": models.Min,
                        "max": models.Max
                    }[column.aggregation](column.path, distinct=True)
                headers.append(column.name)

            qs = [qs.aggregate(**kwargs).values()]

        # aggregates and rows
        else:
            qs = qs.values_list(*[c.path for c in self.columns.filter(aggregation="")])
            headers = [c.name for c in self.columns.filter(aggregation="")]
            for column in self.columns.exclude(aggregation=""):
                kwarg = {
                    column.name: {
                        "sum": models.Sum,
                        "count": models.Count,
                        "min": models.Min,
                        "max": models.Max
                    }[column.aggregation](column.path, distinct=True)
                }
                headers.append(column.name)

                qs = qs.annotate(**kwarg)

            if self.order_by:
                qs = qs.order_by(*self.order_by.split(","))

        # detect foreign keys
        fks = [c.content_type for c in self.columns.all()]

        return headers, qs, fks

    def get_absolute_url(self):
        return reverse("qreports-show-report", args=[self.slug])


class ReportFilter(models.Model):
    report = models.ForeignKey(QueryReport, related_name="filters")
    exclude = models.BooleanField(blank=True, default=False)
    path = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    sort_order = models.SmallIntegerField(default=0)


class ReportColumn(models.Model):

    class Meta(object):
        ordering = ("sort_order",)

    report = models.ForeignKey(QueryReport, related_name="columns")
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    aggregation = models.CharField(max_length=10, choices=(
        ("sum", "Sum"),
        ("count", "Count"),
        ("min", "Minimum"),
        ("max", "Maximum"),
    ), blank=True)
    sort_order = models.SmallIntegerField(default=0)
    rollup = models.BooleanField(default=False)
    format = models.CharField(max_length=255, blank=True)
    alignment = models.CharField(max_length=10, default="left", choices=(
        ("right", "Right"),
        ("center", "Center"),
        ("left", "Left")
    ))

    def get_value(self, object):
        if object:
            if self.aggregation:
                object = getattr(object, self.name, None)
            else:
                for bit in self.path.split("__"):
                    try:
                        object = getattr(object, bit, None)
                    except ObjectDoesNotExist:
                        pass
        return object

    @property
    def content_type(self):

        obj = self.report.base_object.model_class()

        try:
            for subfield in self.path.split("__"):
                next = getattr(obj, subfield, None)

                if isinstance(next, Manager):
                    next = next.get_query_set().model

                if isinstance(next, ReverseSingleRelatedObjectDescriptor):
                    next = next.field.rel.to

                if subfield in ("id", "pk"):
                    break  # keep the current object and stop searching

                elif next:

                    try:
                        field = next._meta.get_field(subfield)
                        if isinstance(field, ForeignKey):
                            next = field.rel.to
                        else:
                            next = None
                    except FieldDoesNotExist:
                        pass

                obj = next

                if not obj:
                    break

        except Exception as ex:
            traceback.print_exc()

        return obj


class ReportVariable(models.Model):
    report = models.ForeignKey(QueryReport, related_name="variables")
    name = models.CharField(max_length=255)
    required = models.BooleanField(blank=True, default=False)
    type = models.CharField(max_length=255, choices=(
        ('value', "Value"),
        ('date', "Date"),
    ))
    initial = models.CharField(max_length=255, blank=True)
