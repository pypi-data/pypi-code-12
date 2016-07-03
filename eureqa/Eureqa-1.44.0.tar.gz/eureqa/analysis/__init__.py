# Copyright (c) 2016, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from eureqa.analysis.components import *
from eureqa.analysis.cards import Card
from eureqa.utils.image import Image

import warnings

class Analysis(object):
    """Represents an analysis on the server.

    :param Eureqa eureqa: A eureqa connection.
    :param dict body: Class metadata as dictionary.

    :var str `~eureqa.analysis.Analysis.name`: The analysis name.
    :var str `~eureqa.analysis.Analysis.description`: The analysis description.
    """

    def __init__(self, body, eureqa):
        """For internal use only"""

        self._id = body['analysis_id']
        self._owner = body['owner']
        self._eureqa = eureqa
        if not 'description' in body:
            body['description'] = ''
        self._body = body

    def url(self):
        return '%s/%s/analyses/%s' % (self._eureqa._session.url, self._eureqa._session.organization, self._id)

    @property
    def _organization(self):
        return self._eureqa._session.organization

    @property
    def name(self):
        """The name of the analysis"""

        return self._body['analysis_name']

    def __repr__(self):
        return "Analysis(" + repr(self.name) + ", ...)"

    @property
    def analysis_id(self):
        """The id of the analysis"""

        return self._id

    @name.setter
    def name(self, value):
        """Change the analysis name to the new value.

        :param str value: The new value for the analysis name.
        """

        self._body['analysis_name'] = value
        self._update()

    @property
    def description(self):
        """The description of the analysis"""

        return self._body['description']

    @description.setter
    def description(self, value):
        """Change the analysis description to the new value.

        :param str value: The new value for the analysis description.
        """

        self._body['description'] = value
        self._update()

    def delete(self):
        """Deletes the analysis from the server."""

        endpoint = '/analysis/%s' % self._id
        self._eureqa._session.report_progress('Deleting analysis: \'%s\'.' % self._id)
        self._eureqa._session.execute(endpoint, 'DELETE')

    def get_cards(self):
        """ Get all Analysis Cards associated with this Analysis

        :return: A list of Card objects that are rendered as part of this Analysis
        :rtype: list of :class:`~eureqa.analysis.cards.Card`
        """
        # Inline import to avoid circular import (Item imports Analysis)
        from .cards import Card
        return sorted(Card._get_all(self), key = lambda c: c._order_index)

    def get_components(self):
        """ Get all Analysis Components associated with this Analysis

        :return: A list of Component objects attached to this Analysis, that may be rendered by Items in the Analysis
        :rtype: list of :class:`~eureqa.analysis.components._Component`
        """
        # Inline import to avoid circular import (Component imports Analysis)
        from .components import _Component
        c = _Component()
        c._analysis = self
        c._eureqa = self._eureqa
        return c._get_all_from_self()

    def _get_component_by_id(self, component_id):
        """ Internal: return the Component object from this analysis with the specified id """
        from .components import _Component
        return _Component._get(analysis=self, component_id=component_id)

    def _create_card(self, title, description, collapse, component):
        body = {
            "title": title,
            "description": description,
            "collapse": collapse,
            "component": component._to_json()
        }
        endpoint = '/analysis/%s/items/create_card_item' % self._id
        results = self._eureqa._session.execute(endpoint, 'POST', body)

        # Split the JSON bundle into a tree of Components and a root Item
        components = {}
        for component_json in results["components"]:
            c = _Component._construct_from_json(component_json, analysis=self)
            components[c._component_id] = c

        # If we have a Component that contains another Component,
        # set up the corresponding Python reference.
        for c in components.itervalues():
            if isinstance(c, TitledLayout):
                c.create_card(components[c._content_component_id])

        card = Card()
        card._from_json(results["item"])
        card.component = components[card._default_component_id]

        return card

    def create_model_card(self, solution, title=None, description=None, collapse=False):
        """Creates a new model card.  Adds the card to this analysis.

        :param eureqa.Solution solution: The solution that will be displayed on the card.
        :param str title: The card title.
        :param str description: The card description.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: An object that represents the newly created card.
        :rtype: ~eureqa.analysis_cards.ModelCard
        """
        component = InteractiveExplainer(solution=solution, search=solution.search,
                                         datasource=self._eureqa.get_data_source_by_id(solution.search._data_source_id))
        return self._create_card(title, description, collapse, component)

    def create_model_summary_card(self, solution, collapse=False):
        """Creates a new model summary card.  Adds the card to this analysis.

        :param eureqa.Solution solution: The solution that will be displayed on the card.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: An object that represents the newly created card.
        :rtype: ~eureqa.analysis_cards.ModelSummaryCard
        """
        # ModelSummaryCards do not have a title or description.
        # So don't use our handy wrapper which automatically creates a TitleLayout.
        from .cards import Card
        component = ModelSummary(analysis=self, solution=solution, search=solution.search,
                                 datasource=self._eureqa.get_data_source_by_id(solution.search._data_source_id))
        return Card(analysis=self, component=component)


    def create_distribution_plot_card(self, data_source, variable, title=None, description=None, collapse=False):
        """Creates a new distribution plot card.  Adds the card to this analysis.

        :param eureqa.DataSource data_source: The data source to which the variable belongs.
        :param str variable: The name of the variable that will be displayed on the card.
        :param str title: The card title.
        :param str description: The card's description.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: An object that represents the newly created card.
        :rtype: ~eureqa.analysis_cards.DistributionPlotCard
        """
        component = VariableDistributionPlot(data_source, variable)
        return self._create_card(title, description, collapse, component)

    def create_text_card(self, text, title='Text', description=None, collapse=False):
        """Creates a new text card.  Adds the card to this analysis.

        :param str text: The card text.
        :param str title: The card title.
        :param str description: Deprecated; unused.  (This card doesn't have a Description.)
        :param bool collapse: Whether the card should default to be collapsed.
        :return: An object that represents the newly created card.
        :rtype: ~eureqa.analysis_cards.TextCard
        """
        component = TextBlock(text)
        return self._create_card(title, description, collapse, component)

    def create_html_card(self, html, title='HTML', description=None, collapse=False):
        """Creates a new HTML card.  Adds the card to this analysis.

        :param str html: The card's HTML body.
        :param str title: The card title.
        :param str description: Deprecated; unused.  (This card doesn't have a Description.)
        :param bool collapse: Whether the card should default to be collapsed.
        :return: An object that represents the newly created card.
        :rtype: ~eureqa.analysis_cards.HtmlCard
        """
        component = HtmlBlock(html)
        return self._create_card(title, description, collapse, component)

    def create_custom_plot_card(self, plot, title=None, description=None, collapse=False):
        """Creates a new custom plot card.  Adds the card to this analysis.

        :param eureqa.analysis.components.CustomPlot plot: The Plot to be displayed in the card.
        :param str title: The card title.
        :param str description: The card's description.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: An object that represents the newly created card.
        :rtype: ~eureqa.analysis_cards.CustomPlotCard
        """

        # First, upload data for the plot
        plot.upload_data(self._eureqa)

        # Then add the plot to the analysis
        return self._create_card(title, description, collapse, plot)

    def create_model_evaluator_card(self, datasource, solution, title=None, description=None, collapse=False):
        """Creates a new model evaluator card.  Adds the card to this analysis.

        :param eureqa.DataSource datasource: DataSource to fetch data from for the primary model evaluator
        :param eureqa.Solution solution: Solution to fetch results from for the primary model evaluator
        :param str title: Title of the card.  Defaults to 'Evaluate Model'.
        :param str description: Description of the card.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card.
        :rtype: ~eureqa.analysis_cards.ModelEvaluatorCard

        Additional models can be added to this model by calling the
        :class:`~eureqa.analysis.ModelEvaluatorCard.add_solution_info` method on
        the returned object.
        """

        if title is None:
            title = "Evaluate Model"

        component = EvaluateModel()
        component.add_solution_info(datasource, solution)
        return self._create_card(title, description, collapse, component)

    def create_box_plot_card(self, datasource, x_var, y_var, title=None, description=None, needs_guides = False, axis_labels=None, label_format=None, collapse=False):
        """Creates a new box-plot card.  Adds the card to this analysis.

        :param eureqa.DataSource datasource: Data source for the card's data
        :param str x_var: The X-axis variable for the card's plot
        :param str y_var: The Y-axis variable for the card's plot
        :param str title: The title of the card
        :param str description: The description of the card
        :param bool needs_guides: Whether the card needs guides
        :param list axis_labels: Axis labels for this card's plot
        :param str label_format: Label format for this card
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.BoxPlotCard
        """
        return self._create_two_variable_plot_card(BoxPlot, datasource, x_var, y_var, title, description,
                                                   needs_guides, axis_labels, label_format, "box plot", collapse)

    def create_double_histogram_plot_card(self, datasource, x_var, y_var, title=None, description=None, needs_guides=False,
                                          axis_labels=None, label_format=None, collapse=False):
        """Creates a new double-histogram card.  Adds the card to this analysis.

        :param eureqa.DataSource datasource: Data source for the card's data
        :param str x_var: The X-axis variable for the card's plot
        :param str y_var: The Y-axis variable for the card's plot
        :param str title: The title of the card
        :param str description: The description of the card
        :param bool needs_guides: Whether the card needs guides
        :param list axis_labels: Axis labels for this card's plot
        :param str label_format: Label format for this card
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.DoubleHistogramPlotCard
        """

        return self._create_two_variable_plot_card(DoubleHistogramPlot, datasource, x_var, y_var, title, description,
                                                   needs_guides, axis_labels, label_format, "histogram plot", collapse)

    def create_scatter_plot_card(self, datasource, x_var, y_var, title=None, description=None, needs_guides=False,
                                 axis_labels=None, label_format=None, collapse=False):
        """Creates a new scatter-plot card.  Adds the card to this analysis.

        :param eureqa.DataSource datasource: Data source for the card's data
        :param str x_var: The X-axis variable for the card's plot
        :param str y_var: The Y-axis variable for the card's plot
        :param str title: The title of the card
        :param str description: The card's description
        :param bool needs_guides: Whether the card needs guides
        :param list axis_labels: Axis labels for this card's plot
        :param list label_format: Label format for this card
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.ScatterPlotCard
        """

        return self._create_two_variable_plot_card(ScatterPlot, datasource, x_var, y_var, title, description,
                                                   needs_guides, axis_labels, label_format, "scatter plot", collapse)

    def create_binned_mean_plot_card(self, datasource, x_var, y_var, title=None, description=None, needs_guides=False,
                                     axis_labels=None, label_format=None, collapse=False):
        """Creates a new binned-mean-plot card.  Adds the card to this analysis.

        :param ~eureqa.DataSource datasource: Data source for the card's data
        :param str x_var: The X-axis variable for the card's plot
        :param str y_var: The Y-axis variable for the card's plot
        :param str title: The title of the card
        :param str description: The card's description.
        :param bool needs_guides: Whether the card needs guides
        :param list axis_labels: Axis labels for this card's plot
        :param list label_format: Label format for this card
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.BinnedMeanPlotCard
        """

        return self._create_two_variable_plot_card(BinnedMeanPlot, datasource, x_var, y_var, title, description,
                                                   needs_guides, axis_labels, label_format, "scatter plot", collapse)

    def _create_two_variable_plot_card(self, plot_type, datasource, x_var, y_var, title=None, description=None,
                                       needs_guides=False, axis_labels=None, label_format=None, card_name="two-variable", collapse=False):

        if axis_labels is None:
            axis_labels = {
                'x': x_var,
                'y': y_var
            }

        if label_format is None:
            default_label_formats = {
                "BOX_PLOT": {'x': 'g', 'y': '.2s'},
                "DOUBLE_HISTOGRAM_PLOT": {'x': '.3s', 'y': 'g'},
                "SCATTER_PLOT": {'x': '.3s', 'y': '.3s'},
                "BINNED_MEAN_PLOT": {'x': '.3s', 'y': '.2f'}
            }

            label_format = default_label_formats.get(plot_type, {
                'x': ".3s",
                'y': ".3s"
            })

        component = plot_type(datasource=datasource,
                              axis_labels=axis_labels,
                              label_format=label_format,
                              needs_guides=needs_guides,
                              x_var=x_var,
                              y_var=y_var)

        return self._create_card(title, description, collapse, component)

    def create_by_row_plot_card(self, datasource, x_var, plotted_vars, title=None, description=None,
                                focus_variable=None, should_center=True, should_scale=False, collapse=False):
        """Create a new by-row plot card.  Adds the card to this analysis.

        :param eureqa.DataSource datasource: Data source for the card's data
        :param str x_var: Name of the variable to plot as the X axis
        :param str plotted_vars: List of string-names of variables to plot.
               (To modify a variable's display name, first create the card; then modify the display name directly on it.)
        :param str title: The card's title.
        :param str description: The card's description.
        :param str focus_variable: Name of the variable in 'plotted_vars' to bring to the foreground
        :param bool should_center: Should the plot be centered?
        :param bool should_scale: Should the plot scale?
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.ByRowPlotCard
        """

        for x in plotted_vars:
            assert isinstance(x, basestring), "'plotted_vars' must be a list of variable-name strings"
        if (not focus_variable) and len(plotted_vars) > 0:
            focus_variable = plotted_vars[0]

        component = VariableLineGraph(datasource, x_var, plotted_vars,
                                      focus_variable, should_center, should_scale)

        return self._create_card(title, description, collapse, component)

    def create_model_fit_by_row_plot_card(self, solution, title=None, description=None, collapse=False, x_axis=None):
        """Create a new model fit by-row plot card.  Adds the card to this analysis.
        Note that by-row plots are meant for use with Numeric searches.  They may not work
        properly if used with other types of searches.

        :param ~eureqa.Solution solution: The Solution object for which this card is being created
        :param str title: The card's title.
        :param str description: The card's description.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.ModelFitByRowPlotCard
        """
        if x_axis is not None:
            warnings.warn("Axis labels are no longer supported by Projection plots", DeprecationWarning)

        component = Projection(solution=solution,
                               search=solution.search,
                               datasource=self._eureqa.get_data_source_by_id(solution.search._data_source_id))

        return self._create_card(title, description, collapse, component)

    def create_model_fit_separation_plot_card(self, solution, title=None, description=None, collapse=False):
        """Create a new model fit separation-plot card.  Adds the card to this analysis.
        Note that separation plots are meant for use with time-series searches.  They may not work
        properly if used with other types of searches.

        :param ~eureqa.Solution solution: The Solution object for which this card is being created
        :param str title: The card's title.
        :param str description: The card's description.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.ModelFitSeparationPlotCard
        """

        component = Centipede(solution=solution,
                              search=solution.search,
                              datasource=self._eureqa.get_data_source_by_id(solution.search._data_source_id))
        return self._create_card(title, description, collapse, component)

    def _get_card_type_from_search_type(self, search_type):
        card_types = {
            "generic": Projection,
            "timeseries": Projection,
            "classification": Centipede,
            "timeseries_classification": Centipede
            }
        return card_types[search_type]

    def _get_card_typename_from_search_type(self, search_type):
        card_typenames = {
            "generic": "model fit by row plot",
            "timeseries": "model fit by row plot",
            "classification": "model fit separation plot",
            "timeseries_classification": "model fit separation plot"
            }
        return card_typenames[search_type]

    def create_model_fit_plot_card(self, solution, x_axis=None, title=None, description=None, collapse=False):
        """Create a new model fit card.  Adds the card to this analysis.
        Automatically choose the correct type of card (by-row plot or separation plot) based on
        the specified search.  Numeric searches use by-row plots; time-series searches use separation plots.

        :param ~eureqa.Solution solution: The Solution object for which this card is being created
        :param str title: The card's title.
        :param str description: The card's description.
        :param bool collapse: Whether the card should default to be collapsed.
        :return: Object representing the created card
        :rtype: ~eureqa.analysis_cards.model_fit_plot_card.ModelFitPlotCard
        """

        if x_axis is not None:
            warnings.warn("Axis labels are no longer supported by Model Fit plots", DeprecationWarning)

        search_type = solution.search._body['search_template_id'].lower()
        card_type = self._get_card_type_from_search_type(search_type)

        component = card_type(solution=solution,
                              search=solution.search,
                              datasource=self._eureqa.get_data_source_by_id(solution.search._data_source_id))

        return self._create_card(title, description, collapse, component)


        card_typename = self._get_card_typename_from_search_type(search_type)
        return self._create_model_fit_plot_card(card_type, solution, title, description, x_axis,
                                                card_typename, collapse)

    def add_card(self, card):
        """ Add an analysis Item to this analysis

        :param eureqa.analysis.cards.Card card: Item to add to the analysis.  Must not already be associated with an Analysis.
        """
        assert getattr(card, "_analysis", self) == self, \
            "'card' must not already be associated with another analysis.  (Did you mean to pass in <card>.clone()?)"
        card._associate(self)

    def create_card(self, component):
        """
        Create a new Card on this Analysis containing the specified Component

        :param component: Component to render inside the Item
        :return: the created Item
        """
        from .cards import Card
        card = Card(component = component)
        self.add_card(card)
        return card

    def html_ref(self, component):
        component._associate(self)

        # Technically you can either add this HtmlBlock, or you can pass in the "analysis"
        # constructor argument back when you created it, or you can add `component` now and add this HtmlBlock later.
        # But if you don't already know that, then you almost certainly just want to add this HtmlBlock.
        assert hasattr(component, "_component_id"), \
            "Add this HtmlBlock to an Analysis (or to another Component that is already on an Analysis) before adding other Components to it"

        return '<nutonian-component id="%s" />' % component._component_id

    def upload_image(self, image_path):
        """Upload an image to the server, to be embedded in analysis cards.

        :param str image_path: the filepath to the image on your filesystem.
        :return: An object that represents the newly uploaded image.
        :rtype: ~eureqa.utils.Image
        """

        image = Image.upload_from_file(self._eureqa, image_path)
        return image

    def create_image_card(self, image_path, title=None, description=None, collapse=False):
        """Creates a new text card containing only header text and one image.

        :param str image_path: the filepath to the image in your filesystem.
        :param str title: The card title.
        :param str description: a description of the card, to appear above the image
        :param bool collapse: Whether the card should default to be collapsed.
        :return: An object that represents the newly created card.
        :rtype: ~eureqa.analysis_cards.TextCard
        """

        if title is None: title = 'Image'

        # upload image to server
        image = self.upload_image(image_path)
        # create text card with embed text for the image
        image_text = ''
        if description is not None:
            image_text += description + '\n\n'
        image_text += '%s' % image
        try:
            return self.create_text_card(image_text, title, description, collapse)
        except Exception as e:
            image.delete()
            raise e

    def _update(self):
        endpoint = '/analysis/%s' % self._id
        self._eureqa._session.report_progress('Updating analysis: \'%s\'.' % self._id)
        new_body = self._eureqa._session.execute(endpoint, 'PUT', self._body)
        new_instance = Analysis(new_body, self._eureqa)
        self.__dict__ = new_instance.__dict__
