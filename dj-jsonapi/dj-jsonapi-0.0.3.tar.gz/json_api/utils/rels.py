
import inspect
from django.utils import six

from . import import_class


class rel(object):
    """
    A generic relationship descriptor.

    *relname* The name of the relationship. Used during serialization.
    *viewset* The viewset that manages the related resource collection.
    *attname* The name used to access the attribute on the resource.
              Defaults to relname if not provided.

    """
    def __init__(self, relname, viewset, attname=None):
        self.relname = relname
        self.viewset = viewset
        self.attname = relname if attname is None else attname

    def viewset():
        def fget(self):
            viewset = self._viewset

            if isinstance(viewset, six.string_types):
                viewset = import_class(viewset)

            if inspect.isclass(viewset):
                viewset = viewset()

            self._viewset = viewset
            return self._viewset

        def fset(self, value):
            self._viewset = value

        return locals()
    viewset = property(**viewset())
