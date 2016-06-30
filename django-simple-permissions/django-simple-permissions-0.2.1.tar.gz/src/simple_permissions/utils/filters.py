# coding=utf-8
"""
Permission filter utilities
"""
import types
from django.db import models


def permission_queryset(self, roles=[], permission=None):
    qs = super(models.Manager, self).get_queryset()
    if roles:
        for logics in self.model._permission_logics:
            print roles, permission
            print logics.list_filter(roles, permission)
            qs = qs.filter(logics.list_filter(roles, permission))
    return qs


def add_permission_filter(model):
    """
    Add permission filter to the model

    Parameters
    ----------
    model : django model class
        A django model class which will be treated by the specified permission
        logic

    Examples
    --------
    >>> from django.db import models
    >>> from simple_permissions.logics import PermissionLogic
    >>> class Mock(models.Model):
    ...     name = models.CharField('name', max_length=120)
    >>> add_permission_logic(Mock, PermissionLogic())
    """
    if not hasattr(model, '_permission_logics'):
        raise AttributeError(
            '`_permission_logics` must be an attribute of %' % model)
    for attr in model.__dict__:
        try:
            manager = getattr(model, attr)
            if not attr.startswith('_') and isinstance(manager, models.Manager):
                manager.permission_filter = types.MethodType(permission_queryset, manager)
        except:
            pass
