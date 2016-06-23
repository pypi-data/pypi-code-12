"""options.py defines the base option classes for steno3d"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from json import dumps
import properties


class Options(properties.PropertyClass):
    """Generic options for all steno3d resources"""

    def as_json(self):
        """returns json representation of options"""
        opts_json = {}
        for key in self._properties:
            opts_json[key] = getattr(self, key)
        return dumps(opts_json)

    @properties.validator
    def validate(self):
        """Check if content is built correctly"""
        return True


class ColorOptions(Options):
    """Options related to resource display color"""
    color = properties.Color(
        'Solid color',
        default='random'
    )
    opacity = properties.Range(
        'Opacity',
        default=1.,
        min_value=0.,
        max_value=1.
    )


class MeshOptions(Options):
    """Options related to mesh display"""
    wireframe = properties.Bool(
        'Wireframe',
        default=False
    )
