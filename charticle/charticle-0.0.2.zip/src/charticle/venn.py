"""Venn diagrams with labeled regions."""
import attr
import matplotlib.pyplot as plt
import matplotlib_venn

from charticle import _validators


@attr.s(slots=True)
class FontSizes(object):
    """Utility class for font size tracking."""
    title = attr.ib(default=20, validator=_validators.positive_int)
    sets = attr.ib(default=14, validator=_validators.positive_int)
    intersections = attr.ib(default=12, validator=_validators.positive_int)


@attr.s(slots=True)
class Venn2(object):
    """Object for a 2-circle Venn.  Set attributes at init or by assignment.

    :param str a_name:
    :param str b_name:  Label text for outside the A & B circles.

    :param str a:
    :param str b: Label text for the 1-member crescents.

    :param str ab: Label text for the lenticular intersection of A & B.

    :param str title: Text for the title of the plot.

    :param palette: a color palette for the A & B sets.
    :type palette: Venn2.Palette

    :param fontsizes: the font sizes for various labels.
    :type fontsizes: FontSizes

    """
    @attr.s(repr_ns="Venn2", slots=True)
    class Palette(object):
        """Container of color palette for both sets.

        :param `a,b`: color names for the two sets.
        :type `a,b`: legal html colornames or hex codes
        :param alpha: color combination alpha for intersection.
        :type alpha: float in [0,1]

        TODO: add some default "constant" palettes.
        """
        a, b = [attr.ib(default=n, validator=_validators.legal_color)
                for n in ('red', 'green')]
        alpha = attr.ib(default=0.4, validator=_validators.zero_to_one)

    @attr.s(repr_ns="Venn2", slots=True)
    class Sizes(object):
        """Utility class for shaping the Venn2."""
        a, b, c, ab, normalize = [
            attr.ib(default=1.0, validator=_validators.non_negative)
            for _ in range(5)]

        def to_dict(self):
            return {
                '10': self.a, '01': self.b, '11': self.ab,
            }

    a_name, b_name = [attr.ib(default=None,
                              validator=_validators.optional_string)
                      for n in ('A', 'B')]
    a, b, ab = [attr.ib(default=None, validator=_validators.optional_string)
                for n in ('a', 'b', 'ab')]
    title = attr.ib(default=None, validator=_validators.optional_string)

    sizes = attr.ib(default=attr.Factory(Sizes))
    fontsizes = attr.ib(default=attr.Factory(FontSizes))
    palette = attr.ib(default=attr.Factory(Palette))

    def plot(self, ax=None):
        """Produce a plot on the specified axes.

        Puts label strings in the right places and produces the figure.

        ax: the axis on which to plot this diagram. Defaults to current axes.
        """
        if ax is None:
            ax = plt.axes()

        attr.validate(self)
        attr.validate(self.sizes)
        attr.validate(self.palette)
        attr.validate(self.fontsizes)

        # Adjust the relative size of the areas so that there is more
        # space in the outer ones.
        v = matplotlib_venn.venn2(
            # region sizes,
            subsets=self.sizes.to_dict(), normalize_to=self.sizes.normalize,
            # region colors,
            set_colors=(self.palette.a, self.palette.b),
            alpha=self.palette.alpha,
            ax=ax)

        # String 'A', 'B', 'C', are the outer set label names declared
        # by matplotlib_venn.
        for label, val in (('A', self.a_name), ('B', self.b_name)):
            t = v.get_label_by_id(label)
            t.set_text("" if val is None else val)
            t.set_fontsize(self.fontsizes.sets)

        # Numeric strings are the labels for the intersecting regions
        # declared by matplotlib_venn
        for label, val in (
                ('10', self.a), ('01', self.b), ('11', self.ab)):
            t = v.get_label_by_id(label)
            if t is None:
                continue
            t.set_text("" if val is None else val)
            t.set_fontsize(self.fontsizes.intersections)

        if self.title:
            ax.set_title(self.title, size=self.fontsizes.title)

        return v


@attr.s(slots=True)
class Venn3(object):
    """Object for a 3-label venn.  Set attributes at init or by assignment.

    :param str a_name:
    :param str b_name:
    :param str c_name:  Label text for the outer circles.

    :param str a:
    :param str b:
    :param str c: Label text for the 1-member patches.

    :param str ab:
    :param str ac:
    :param str bc: Label text for the 2-set-intersection patches.

    :param str abc: Label text for the full 3-set intersection.

    :param str title: Text for the title of the plot.

    :param palette: a color palette for the sets.
    :type palette: Venn3.Palette

    :param sizes: the region sizes (relative to 1.0).
    :type sizes: Venn3.Sizes

    :param fontsizes: the font sizes for various labels.
    :type fontsizes: FontSizes

    """

    @attr.s(repr_ns="Venn3", slots=True)
    class Sizes(object):
        """Utility class for shaping the Venn3."""
        a, b, c, ab, ac, bc, abc, normalize = [
            attr.ib(default=1.0, validator=_validators.non_negative)
            for _ in range(8)]

        def set_double_weight(self, weight):
            self.bc = self.ac = self.ab = weight
            return self

        def set_single_weight(self, weight):
            self.a = self.b = self.c = weight
            return self

        def to_dict(self):
            return {
                '100': self.a, '010': self.b, '001': self.c,
                '011': self.bc, '101': self.ac, '110': self.ab,
                '111': self.abc
            }

    @attr.s(repr_ns="Venn3", slots=True)
    class Palette(object):
        """Container of color palette for all 3 items.

        :param `a,b,c`: color names for the three sets.
        :type `a,b,c`: legal html colornames or hex codes
        :param alpha: color combination alpha for intersections.
        :type alpha: float in [0,1]

        TODO: add some default "constant" palettes.
        """
        a, b, c = [attr.ib(default=n, validator=_validators.legal_color)
                   for n in ('red', 'green', 'blue')]
        alpha = attr.ib(default=0.4, validator=_validators.zero_to_one)

    a_name, b_name, c_name = [attr.ib(default=None,
                                      validator=_validators.optional_string)
                              for n in ('A', 'B', 'C')]
    a, b, c = [attr.ib(default=None, validator=_validators.optional_string)
               for n in ('a', 'b', 'c')]
    ab, bc, ac = [attr.ib(default=None, validator=_validators.optional_string)
                  for n in ('a & b', 'b & c', 'a & c')]
    abc = attr.ib(default=None,
                  validator=_validators.optional_string)
    title = attr.ib(default=None, validator=_validators.optional_string)

    sizes = attr.ib(default=attr.Factory(Sizes))
    fontsizes = attr.ib(default=attr.Factory(FontSizes))
    palette = attr.ib(default=attr.Factory(Palette))

    def plot(self, ax=None):
        """Produce a plot on the specified axes.

        Puts label strings in the right places and produces the figure.

        ax: the axis on which to plot this diagram. Defaults to current axes.
        """
        if ax is None:
            ax = plt.axes()

        attr.validate(self)
        attr.validate(self.sizes)
        attr.validate(self.palette)
        attr.validate(self.fontsizes)
        # Adjust the relative size of the areas so that there is more
        # space in the outer ones.
        v = matplotlib_venn.venn3(
            # region sizes,
            subsets=self.sizes.to_dict(), normalize_to=self.sizes.normalize,
            # region colors,
            set_colors=(self.palette.a, self.palette.b, self.palette.c),
            alpha=self.palette.alpha,
            ax=ax)

        # String 'A', 'B', 'C', are the outer set label names declared
        # by matplotlib_venn.
        for label, val in (('A', self.a_name), ('B', self.b_name),
                           ('C', self.c_name)):
            t = v.get_label_by_id(label)
            t.set_text("" if val is None else val)
            t.set_fontsize(self.fontsizes.sets)

        # Numeric strings are the labels for the intersecting regions
        # declared by matplotlib_venn
        for label, val in (
                ('100', self.a), ('010', self.b), ('001', self.c),
                ('110', self.ab), ('011', self.bc), ('101', self.ac),
                ('111', self.abc)):
            t = v.get_label_by_id(label)
            if t is None:
                continue  # no such region.
            t.set_text("" if val is None else val)
            t.set_fontsize(self.fontsizes.intersections)

        if self.title:
            ax.set_title(self.title, size=self.fontsizes.title)

        return v
