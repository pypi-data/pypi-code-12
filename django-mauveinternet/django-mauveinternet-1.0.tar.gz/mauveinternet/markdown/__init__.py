import django.db.models
from .util import MarkdownTextarea # for compatibility

from django.utils.text import capfirst

# Global dict of configured linkable objects
_link_providers = {}


def register_linkable(model_or_queryset):
    try:
        if issubclass(model_or_queryset, django.db.models.Model):
            model = model_or_queryset
            _link_providers[model] = model._default_manager
            return
    except TypeError:
        pass

    queryset = model_or_queryset
    model = queryset.model
    _link_providers[model] = queryset


def get_models():
    """Return a list of linkable ('appname.Model', 'Verbose name') pairs."""
    return [('%s.%s' % (m._meta.app_label, m._meta.object_name), capfirst(m._meta.verbose_name)) for m in _link_providers]


def get_model(mname):
    """Return a linkable model for the given 'appname.Model' string"""
    for m in _link_providers:
        if mname == ('%s.%s' % (m._meta.app_label, m._meta.object_name)):
            return m, _link_providers[m].all()
    raise ValueError("No linkable model found matching '%s'" % mname)
