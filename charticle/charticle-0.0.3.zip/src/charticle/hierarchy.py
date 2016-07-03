import matplotlib
from matplotlib import pyplot as plt

import math
import numpy
import attr.validators
import cycler
from charticle import _validators


@attr.s
class Hierarchy(object):
    """Draws a 'Maslow-style' hierarchy."""
    scale = attr.ib(default=1.0, validator=_validators.positive)
    polygon = attr.ib(default=attr.Factory(dict))
    DEFAULT_COLOR_CYCLE = ('red', 'orange', 'yellow',
                           'green', 'blue', 'purple')

    layers = attr.ib(default=attr.Factory(list))
    layer_polygon_defaults = attr.ib(default=attr.Factory(dict))
    layer_text_defaults = attr.ib(default=attr.Factory(dict))
    color_cycle = attr.ib(
        default=cycler.cycler(color=DEFAULT_COLOR_CYCLE),
        validator=attr.validators.instance_of(cycler.Cycler))

    @attr.s(repr_ns="Hierarchy", slots=True)
    class Layer(object):
        """Container for layer information."""
        label = attr.ib(validator=_validators.is_string)
        lower, upper = [attr.ib(validator=_validators.zero_to_one)
                        for _ in range(2)]
        polygon = attr.ib(default=attr.Factory(dict))
        text = attr.ib(default=attr.Factory(dict))

        def plot(self, hierarchy, ax, default_color=None):
            """Adds this layer to the hierarchy."""
            def h_offset(p):
                return hierarchy.scale * (1.0 - p)

            def v_offset(v):
                return hierarchy.altitude * v

            # Compute corners of trapezoid
            upper_left = (-h_offset(self.upper), v_offset(self.upper))
            upper_right = (h_offset(self.upper), v_offset(self.upper))
            lower_left = (-h_offset(self.lower), v_offset(self.lower))
            lower_right = (h_offset(self.lower), v_offset(self.lower))

            corners = [lower_left, lower_right, upper_right, upper_left]

            # Labels should go at 1/3 of height; especially important
            # in upper layers.
            v_centroid = v_offset(numpy.mean([self.upper,
                                              self.lower, self.lower]))

            poly_args = dict(color=default_color)

            if hierarchy.layer_polygon_defaults:
                poly_args.update(hierarchy.layer_polygon_defaults)

            if self.polygon:
                poly_args.update(self.polygon)
            poly = plt.Polygon(corners, closed=True, **poly_args)

            ax.add_patch(poly)
            text_args = dict(verticalalignment='center',
                             horizontalalignment='center')

            text_args.update(hierarchy.layer_text_defaults)

            text_args.update(self.text)
            ax.text(x=0, y=v_centroid, s=self.label, **text_args)

    @property
    def altitude(self):
        return math.sqrt(3.0) * self.scale

    @property
    def triangle(self):
        poly_args = dict(fill=False)
        poly_args.update(self.polygon)
        return plt.Polygon([(-self.scale, 0), (self.scale, 0),
                            (0, self.altitude)],
                           closed=True, **poly_args)

    def add_layer(self, **kwargs):
        l = self.Layer(**kwargs)
        self.layers.append(l)
        return l

    def set_color_cycle(self, *colors):
        """Sets color cycle from iterable of color names.

        :param colors: color names or None.
        :type colors: valid matplotlib color names.
        """
        self.color_cycle = cycler.cycler(color=colors)
        attr.validate(self)

    def plot(self, ax=None):
        """Write the hierarchy (onto specified axes, if given)."""
        if ax is None:
            ax = matplotlib.pyplot.gca()
        ax.set_aspect('equal', 'datalim')
        ax.add_patch(self.triangle)
        for l, c in zip(self.layers, self.color_cycle):
            attr.validate(l)
            l.plot(hierarchy=self, default_color=c['color'], ax=ax)

    def set_layers(self, layers_list):
        """Write text labels into parameters."""
        intervals = numpy.linspace(0.0, 1.0,
                                   num=len(layers_list) + 1,
                                   endpoint=True)

        for bottom, top, label in zip(intervals[:-1],
                                      intervals[1:], layers_list):
            self.add_layer(lower=bottom, upper=top, label=label)
        return self.layers
