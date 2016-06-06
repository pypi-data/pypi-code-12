# coding=utf-8
"""
permission_required decorator for generic classbased view from django 1.3
"""
from functools import wraps
from django.utils.decorators import available_attrs
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, BaseCreateView, BaseUpdateView, BaseDeleteView
from simple_permissions.decorators.utils import redirect_to_login


def permission_required(perm=None, queryset=None,
                        login_url=None, raise_exception=False):
    """
    Permission check decorator for classbased generic view

    This decorator works as class decorator
    DO NOT use ``method_decorator`` or whatever while this decorator will use
    ``self`` argument for method of classbased generic view.

    Parameters
    ----------
    perm : string
        A permission string
    queryset_or_model : queryset or model
        A queryset or model for finding object.
        With classbased generic view, ``None`` for using view default queryset.
        When the view does not define ``get_queryset``, ``queryset``,
        ``get_object``, or ``object`` then ``obj=None`` is used to check
        permission.
        With functional generic view, ``None`` for using passed queryset.
        When non queryset was passed then ``obj=None`` is used to check
        permission.

    Examples
    --------
    >>> @permission_required('write')
    >>> class UpdateAuthUserView(UpdateView):
    ...     pass
    """

    def wrapper(cls):
        def dispatch_wrapper(view_func):
            @wraps(view_func, assigned=available_attrs(view_func))
            def inner(self, request, *args, **kwargs):
                obj = get_object_from_classbased_instance(self, queryset, request, *args, **kwargs)
                model = type(obj)
                has_perm = True
                if hasattr(model, '_permission_logics'):
                    permission = perm
                    if permission is None:
                        if issubclass(cls, CreateView) | issubclass(cls, UpdateView) | issubclass(cls, DeleteView):
                            permission = 'write'
                        elif issubclass(cls, DetailView) | issubclass(cls, ListView):
                            permission = 'read'
                        elif issubclass(cls, BaseCreateView) | issubclass(cls, BaseUpdateView) | issubclass(cls, BaseDeleteView):
                            permission = 'write'
                        elif issubclass(cls, BaseDetailView) | issubclass(cls, BaseListView):
                            permission = 'read'
                        else:
                            return PermissionDenied
                    has_perm = all([logics.has_perm(request, permission, obj=obj) for logics in model._permission_logics])

                if not has_perm:
                    if raise_exception:
                        raise PermissionDenied
                    else:
                        return redirect_to_login(request, login_url)
                return view_func(self, request, *args, **kwargs)
            return inner

        def get_queryset_wrapper(view_func):
            @wraps(view_func, assigned=available_attrs(view_func))
            def inner(self, *args, **kwargs):
                qs = view_func(self, *args, **kwargs)
                model = self.model
                if hasattr(model, '_permission_logics'):
                    permission = perm
                    roles = self.request.user.roles.all()
                    for logics in self.model._permission_logics:
                        qs = qs.filter(logics.list_filter(roles, permission))
                return qs
            return inner

        cls.dispatch = dispatch_wrapper(cls.dispatch)
        if hasattr(cls, 'get_queryset') and issubclass(cls, BaseListView):
            cls.get_queryset = get_queryset_wrapper(cls.get_queryset)
        return cls

    return wrapper


def get_object_from_classbased_instance(
        instance, queryset, request, *args, **kwargs):
    """
    Get object from an instance of classbased generic view

    Parameters
    ----------
    instance : instance
        An instance of classbased generic view
    queryset : instance
        A queryset instance
    request : instance
        A instance of HttpRequest

    Returns
    -------
    instance
        An instance of model object or None
    """
    # initialize request, args, kwargs of classbased_instance
    # most of methods of classbased view assumed these attributes
    # but these attributes is initialized in ``dispatch`` method.
    instance.request = request
    instance.args = args
    instance.kwargs = kwargs

    # get queryset from class if ``queryset_or_model`` is not specified
    if hasattr(instance, 'get_queryset') and not queryset:
        queryset = instance.get_queryset()
    elif hasattr(instance, 'queryset') and not queryset:
        queryset = instance.queryset
    elif hasattr(instance, 'model') and not queryset:
        queryset = instance.model._default_manager.all()

    # get object
    if hasattr(instance, 'get_object'):
        try:
            obj = instance.get_object(queryset)
        except AttributeError as e:
            # CreateView has ``get_object`` method but CreateView
            # should not have any object before thus simply set
            # None
            if isinstance(instance, BaseCreateView):
                obj = None
            else:
                raise e
    elif hasattr(instance, 'object'):
        obj = instance.object
    else:
        obj = None
    return obj
