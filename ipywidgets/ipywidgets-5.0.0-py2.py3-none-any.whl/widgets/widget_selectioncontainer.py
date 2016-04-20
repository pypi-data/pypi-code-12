"""SelectionContainer class.

Represents a multipage container that can be used to group other widgets into
pages.
"""

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from .widget_box import Box, register
from traitlets import Unicode, Dict, CInt


class _SelectionContainer(Box):
    """Base class used to display multiple child widgets."""
    _model_module = Unicode('jupyter-js-widgets').tag(sync=True)
    _view_module = Unicode('jupyter-js-widgets').tag(sync=True)

    _titles = Dict(help="Titles of the pages").tag(sync=True)
    selected_index = CInt().tag(sync=True)

    # Public methods
    def set_title(self, index, title):
        """Sets the title of a container page.

        Parameters
        ----------
        index : int
            Index of the container page
        title : unicode
            New title
        """
        self._titles[index] = title
        self.send_state('_titles')

    def get_title(self, index):
        """Gets the title of a container pages.

        Parameters
        ----------
        index : int
            Index of the container page
        """
        if index in self._titles:
            return self._titles[index]
        else:
            return None


@register('Jupyter.Accordion')
class Accordion(_SelectionContainer):
    """Displays children each on a separate accordion page."""
    _view_name = Unicode('AccordionView').tag(sync=True)
    _model_name = Unicode('AccordionModel').tag(sync=True)


@register('Jupyter.Tab')
class Tab(_SelectionContainer):
    """Displays children each on a separate accordion tab."""
    _view_name = Unicode('TabView').tag(sync=True)
    _model_name = Unicode('TabModel').tag(sync=True)
