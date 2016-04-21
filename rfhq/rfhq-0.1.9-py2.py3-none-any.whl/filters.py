# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import inflection


class FilterOptionsMixin(object):

    view_options_defaults = {}

    @property
    def view_options_property(self):
        return "{}_options".format(inflection.underscore(self.__class__.__name__))

    def get_options(self, view):
        if not hasattr(self, '_options'):
            self._options = {}
            self._options.update(self.view_options_defaults)
            self._options.update(getattr(view, self.view_options_property, {}))
        return self._options

    def get_option(self, view, option, default=None):
        return self.get_options(view).get(option, default)

