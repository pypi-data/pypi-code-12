# coding=utf-8
import json
import datetime
from django.core.exceptions import FieldDoesNotExist, ValidationError

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import six


def to_dict(obj, excludes=None):
    """
    转换为dict类型
    :param obj: 
    :return:
    """
    d = {}
    excludes = excludes or []

    def dump_submodel(sub_obj):
        sd = {}
        for fd in sub_obj._meta.fields:
            if isinstance(fd, models.DurationField):
                sd[fd.name] = fd.value_to_string(fd)
            elif not isinstance(fd, models.ManyToManyField):
                sd[fd.name] = fd.value_to_string(fd)
        return sd

    for field in obj._meta.fields:
        if field.name in excludes:
            continue
        if isinstance(field, models.ForeignKey):
            d['{}_id'.format(field.name)] = getattr(obj, '%s_id' % field.name)
        elif isinstance(field, models.ManyToManyField):
            field_attr = getattr(obj, field.name, field.get_attname())
            d[field.name] = [dump_submodel(o) for o in field_attr.all()]
        elif isinstance(field, models.FileField):
            if getattr(obj, field.name):
                d[field.name] = getattr(obj, field.name).name
                d['%s_url' % field.name] = getattr(obj, field.name).url
        elif isinstance(field, models.DurationField):
            d[field.name] = field.value_to_string(obj)
        else:
            d[field.name] = getattr(obj, field.name)
    return d


def to_json(obj):
    """
    转换为json
    :param obj:
    :return:
    """
    return json.dumps(to_dict(obj), cls=DjangoJSONEncoder)


def from_dict(d, cls):
    """
    从dict恢复
    :param d:
    :param cls:
    :return:
    """
    if 'id' in d:
        try:
            obj = cls.objects.get(id=d['id'])
        except cls.DoesNotExist:
            obj = cls()
    else:
        obj = cls()
    for k, v in d.iteritems():
        if hasattr(obj, k) and not isinstance(v, list):
            try:
                field = obj._meta.get_field(k)

                if isinstance(field, models.DurationField):
                    if v == '':
                        setattr(obj, k, datetime.timedelta())
                    else:
                        value = field.to_python(v)
                        setattr(obj, k, value)
                else:
                    value = field.to_python(v)
                    setattr(obj, k, value)
            except (FieldDoesNotExist, ValidationError):
                pass
    return obj


def from_json(jso, cls):
    """
    从json转换
    :param jso:
    :param cls:
    :return:
    """
    d = json.loads(jso) if isinstance(jso, six.string_types) else jso
    return from_dict(d, cls)

