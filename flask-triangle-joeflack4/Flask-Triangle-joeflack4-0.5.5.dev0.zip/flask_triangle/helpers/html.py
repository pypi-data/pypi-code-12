# -*- encoding: utf-8 -*-
"""
    flask_triangle.helpers.html
    ---------------------------

    :copyright: (c) 2013 by Morgan Delahaye-Prat.
    :license: BSD, see LICENSE for more details.
"""


<<<<<<< HEAD
from __future__ import absolute_import, division, print_function, unicode_literals
=======
from __future__ import absolute_import
from __future__ import unicode_literals

import sys, re
from six import text_type


class HTMLAttrs(object):
    """
    """
>>>>>>> 4e2abbf8e43dd46234642445e69e0ac2683425b4

try:
    class HTMLString(unicode):
        """
        A `unicode` string considered as sage HTML.
        """
        def __html__(self):
            return self
except:
    class HTMLString(str):
        """
        A `unicode` string considered as sage HTML.
        """
<<<<<<< HEAD
        def __html__(self):
            return self
=======
        Render one attribute as expected in the HTML.
        - key="value"
        """

        if value is None:
            return name
        return '{name}={value}'.format(name=name,
                                       value=HTMLAttrs.attr_value(value))

    def __init__(self, **kwargs):

        self.attributes = dict()

        for k, v in kwargs.items():
            self[k] = v

    def items(self):
        return self.attributes.items()

    def get(self, key, default):
        return self.attributes.get(self.attr_name(key), default)

    def __contains__(self, key):
        return self.attr_name(key) in self.attributes

    def __getitem__(self, key):
        return self.attributes[self.attr_name(key)]

    def __setitem__(self, key, value):
        self.attributes[self.attr_name(key)] = value

    def __delitem__(self, key):
        del self.attributes[self.attr_name(key)]

    def __iter__(self):
        return self.attributes.__iter__()

    def __unicode__(self):
        return ' '.join(self.render_attr(k, v) for k, v in sorted(self.items()))

    def __str__(self): # pragma: no cover
        # Python2/3 compatibility
        if sys.version_info > (3, 0):
            return self.__unicode__()
        return unicode(self).encode('utf-8')

    def update(self, kvp_iterable):
        for k, v in kvp_iterable.items():
            self[k] = v


class HTMLString(text_type):

    def __html__(self):  # pragma: no cover
        return self
>>>>>>> 4e2abbf8e43dd46234642445e69e0ac2683425b4
