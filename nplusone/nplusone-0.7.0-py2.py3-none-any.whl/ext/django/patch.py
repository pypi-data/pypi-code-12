# -*- coding: utf-8 -*-

import copy
import inspect
import functools
import importlib
import itertools
import threading

import django
from django.db.models import query
from django.db.models import Model

from nplusone.core import signals

if django.VERSION >= (1, 9):  # pragma: no cover
    from django.db.models.fields.related_descriptors import (
        ReverseOneToOneDescriptor,
        ForwardManyToOneDescriptor,
        create_reverse_many_to_one_manager,
        create_forward_many_to_many_manager,
    )
else:  # pragma: no cover
    from django.db.models.fields.related import (
        SingleRelatedObjectDescriptor as ReverseOneToOneDescriptor,
        ReverseSingleRelatedObjectDescriptor as ForwardManyToOneDescriptor,
        create_foreign_related_manager as create_reverse_many_to_one_manager,
        create_many_related_manager as create_forward_many_to_many_manager,
    )


def get_worker():
    return str(threading.current_thread().ident)


def setup_state():
    signals.get_worker = get_worker
setup_state()


def to_key(instance):
    model = type(instance)
    return ':'.join([model.__name__, format(instance.pk)])


def patch(original, patched):
    module = importlib.import_module(original.__module__)
    setattr(module, original.__name__, patched)


def signalify_queryset(func, parser=None, **context):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        queryset = func(*args, **kwargs)
        ctx = copy.copy(context)
        ctx['args'] = context.get('args', args)
        ctx['kwargs'] = context.get('kwargs', kwargs)
        queryset._clone = signalify_queryset(queryset._clone, parser=parser, **ctx)
        queryset.iterator = signals.signalify(
            signals.lazy_load,
            queryset.iterator,
            parser=parser,
            **ctx
        )
        queryset._context = ctx
        return queryset
    return wrapped


def get_related_name(model):
    return '{0}_set'.format(model._meta.model_name)


def parse_field(field):
    return (
        (
            field.rel.model  # Django >= 1.8
            if hasattr(field.rel, 'model')
            else field.related_field.model  # Django <= 1.8
        ),
        field.rel.related_name or get_related_name(field.rel.related_model),
    )


def parse_reverse_field(field):
    return field.model, field.name


def parse_related(context):
    if 'rel' in context:  # pragma: no cover
        rel = context['rel']
        return parse_related_parts(rel.model, rel.related_name, rel.related_model)
    else:  # pragma: no cover
        field = context['rel_field']
        model = field.related_field.model
        related_name = field.rel.related_name
        related_model = context['rel_model']
        return parse_related_parts(model, related_name, related_model)


def parse_related_parts(model, related_name, related_model):
    return (
        model,
        related_name or get_related_name(related_model),
    )


def parse_reverse_one_to_one_queryset(args, kwargs, context):
    descriptor = context['args'][0]
    field = descriptor.related.field
    model, name = parse_field(field)
    instance = context['kwargs']['instance']
    return model, to_key(instance), name


def parse_forward_many_to_one_queryset(args, kwargs, context):
    descriptor = context['args'][0]
    instance = context['kwargs']['instance']
    return descriptor.field.model, to_key(instance), descriptor.field.name


def parse_many_related_queryset(args, kwargs, context):
    rel = context['rel']
    manager = context['args'][0]
    model = manager.instance.__class__
    related_model = (
        manager.target_field.related_model  # Django >= 1.8
        if hasattr(manager.target_field, 'related_model')
        else manager.target_field.related_field.model  # Django <= 1.8
    )
    field = manager.prefetch_cache_name if rel.related_name else None
    return (
        model,
        to_key(manager.instance),
        field or get_related_name(related_model),
    )


def parse_foreign_related_queryset(args, kwargs, context):
    model, name = parse_related(context)
    descriptor = context['args'][0]
    return model, to_key(descriptor.instance), name


query.prefetch_one_level = signals.designalify(
    signals.lazy_load,
    query.prefetch_one_level,
)


ReverseOneToOneDescriptor.get_queryset = signalify_queryset(
    ReverseOneToOneDescriptor.get_queryset,
    parser=parse_reverse_one_to_one_queryset,
)
ForwardManyToOneDescriptor.get_queryset = signalify_queryset(
    ForwardManyToOneDescriptor.get_queryset,
    parser=parse_forward_many_to_one_queryset,
)


def _create_forward_many_to_many_manager(*args, **kwargs):
    context = inspect.getcallargs(create_forward_many_to_many_manager, *args, **kwargs)
    manager = create_forward_many_to_many_manager(*args, **kwargs)
    manager.get_queryset = signalify_queryset(
        manager.get_queryset,
        parser=parse_many_related_queryset,
        **context
    )
    return manager
patch(create_forward_many_to_many_manager, _create_forward_many_to_many_manager)


def _create_reverse_many_to_one_manager(*args, **kwargs):
    context = inspect.getcallargs(create_reverse_many_to_one_manager, *args, **kwargs)
    manager = create_reverse_many_to_one_manager(*args, **kwargs)

    manager.get_queryset = signalify_queryset(
        manager.get_queryset,
        parser=parse_foreign_related_queryset,
        **context
    )
    return manager
patch(create_reverse_many_to_one_manager, _create_reverse_many_to_one_manager)


def parse_forward_many_to_one_get(args, kwargs, context):
    descriptor, instance, _ = args
    if instance is None:
        return None
    field, model = parse_reverse_field(descriptor.field)
    return field, model, [to_key(instance)]


ForwardManyToOneDescriptor.__get__ = signals.signalify(
    signals.touch,
    ForwardManyToOneDescriptor.__get__,
    parser=parse_forward_many_to_one_get,
)


def parse_reverse_one_to_one_get(args, kwargs, context):
    descriptor, instance = args[:2]
    if instance is None:
        return None
    model, field = parse_field(descriptor.related.field)
    return model, field, [to_key(instance)]


ReverseOneToOneDescriptor.__get__ = signals.signalify(
    signals.touch,
    ReverseOneToOneDescriptor.__get__,
    parser=parse_reverse_one_to_one_get,
)


def parse_iterate_queryset(args, kwargs, context):
    self = args[0]
    if hasattr(self, '_context'):
        manager = self._context['args'][0]
        instance = manager.instance
        # Handle iteration over many-to-many relationship
        if manager.__class__.__name__ == 'ManyRelatedManager':
            rel = self._context['rel']
            return (
                instance.__class__,
                rel.related_name or get_related_name(rel.related_model),
                [to_key(instance)],
            )
        # Handle iteration over one-to-many relationship
        else:
            model, field = parse_related(self._context)
            return model, field, [to_key(instance)]


def parse_load(args, kwargs, context, ret):
    return [
        to_key(row)
        for row in ret
        if isinstance(row, Model)
    ]


def is_single(low, high):
    return high is not None and high - low == 1


# Emit `touch` on iterating prefetched `QuerySet` instances
original_iterate_queryset = query.QuerySet.__iter__
def iterate_queryset(self):
    if self._prefetch_done:
        signals.touch.send(
            get_worker(),
            args=(self, ),
            parser=parse_iterate_queryset,
        )
    ret, clone = itertools.tee(original_iterate_queryset(self))
    if not is_single(self.query.low_mark, self.query.high_mark):
        signals.load.send(
            get_worker(),
            args=(self, ),
            ret=list(clone),
            parser=parse_load,
        )
    return ret
query.QuerySet.__iter__ = iterate_queryset


original_related_populator_init = query.RelatedPopulator.__init__
def related_populator_init(self, *args, **kwargs):
    original_related_populator_init(self, *args, **kwargs)
    self.__nplusone__ = {
        'args': args,
        'kwargs': kwargs,
    }
query.RelatedPopulator.__init__ = related_populator_init


def parse_eager_select(args, kwargs, context):
    populator = args[0]
    instance = args[2]
    meta = populator.__nplusone__
    klass_info, select, _ = meta['args']
    field = klass_info['field']
    model, name = (
        parse_field(field)
        if klass_info['reverse']
        else parse_reverse_field(field)
    )
    return model, name, [to_key(instance)], id(select)


# Emit `eager_load` on populating from `select_related`
query.RelatedPopulator.populate = signals.signalify(
    signals.eager_load,
    query.RelatedPopulator.populate,
    parser=parse_eager_select,
)


def parse_eager_join(args, kwargs, context):
    instances, descriptor, fetcher, _ = args
    model = instances[0].__class__
    field = fetcher.prefetch_to
    keys = [to_key(instance) for instance in instances]
    return model, field, keys, id(instances)


# Emit `eager_load` on populating from `prefetch_related`
query.prefetch_one_level = signals.signalify(
    signals.eager_load,
    query.prefetch_one_level,
    parser=parse_eager_join,
)


# Emit `touch` on indexing into prefetched `QuerySet` instances
original_getitem_queryset = query.QuerySet.__getitem__
def getitem_queryset(self, index):
    if self._prefetch_done:
        signals.touch.send(
            get_worker(),
            args=(self, ),
            parser=parse_iterate_queryset,
        )
    return original_getitem_queryset(self, index)
query.QuerySet.__getitem__ = getitem_queryset
