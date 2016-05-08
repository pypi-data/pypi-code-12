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

from analysis_card import AnalysisCard

class TwoVariablePlot(AnalysisCard):
    """Represents a two-variable plot.  Common base class for two-variable plots.

    :param DataSource datasource: The data source containing the data to be plotted.
    :param str x_var: The X-axis variable for the card's plot.
    :param str y_var: The Y-axis variable for the card's plot.
    :param str title: The title of the card.
    :param str description: A textual description of the card.
    :param bool needs_guides: Whether the card needs guides.
    :param XYMap axis_labels: Axis labels for this card's plot.  Set member fields "x" and "y" to set the X and Y axis labels.
    :param XYMap label_format: Label format for this card.  Set member fields "x" and "y" to set the X and Y axis printf-style format-strings; for example, ".3s".
    :param bool collapse: Whether the card should default to be collapsed.

    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlotCard.title: The title of the card
    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlotCard.x_var: The X-axis variable for the card's plot
    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlotCard.y_var: The Y-axis variable for the card's plot
    :var bool ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlotCard.needs_guides: Whether the card needs guides
    :var XYMap ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlotCard.axis_labels: Axis labels for this card's plot.  Set member fields "x" and "y" to set the X and Y axis labels.
    :var XYMap ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlotCard.label_format: Label format for this card.  Set member fields "x" and "y" to set the X and Y axis printf-style format-strings; for example, ".3s".
    """

    def __init__(self,  datasource=None, x_var=None, y_var=None, title=None, description=None,
                 needs_guides=False,axis_labels=None, label_format=None, collapse=False):
        """ TwoVariablePlot init """
        super(TwoVariablePlot, self).__init__()

        self.datasource = datasource
        self.title = title
        self.description = description
        self.x_var = x_var
        self.y_var = y_var
        self.needs_guides = needs_guides
        self.collapse = collapse

        if axis_labels:
            self.axis_labels = axis_labels
        if label_format:
            self.label_format = label_format


    class XYMap(object):
        """ A named tuple with keys 'x' and 'y' 

        :param TwoVariablePlotCard tvp: The TwoVariablePlotCard object.
        :param dict dic: X and Y parameters as dictionary.
        """
        def __init__(self, tvp, dic):
            self._tvp = tvp
            self._dic = dic

        @property
        def x(self):
            """ X value """
            return self._dic['x']

        @x.setter
        def x(self, val):
            self._dic['x'] = val
            self._tvp._update_card()

        @property
        def y(self):
            """ Y value """
            return self._dic['y']

        @y.setter
        def y(self, val):
            self._dic['y'] = val
            self._tvp._update_card()

    @property
    def datasource(self):
        """The data source providing data for this card

        :return: data source providing data for this card
        """
        if len(self._body['dependencies']) == 0:
            return None
        return self._eureqa._get_data_source_from_id(self._body['dependencies'][0]['datasource_id'])

    @datasource.setter
    def datasource(self, val):
        self._body['dependencies'] = [{"datasource_id": val._data_source_id}] if val else []

    @property
    def title(self):
        """The title of this card.

        :return: title of this card
        :rtype: str"""
        return self._body['content']['title'] if 'title' in self._body['content'] else None

    @title.setter
    def title(self, value):
        self._body['content']['title'] = value
        self._update_card()

    @property
    def description(self):
        """ The description of this card.

        :return: description of this card
        :rtype: str"""
        return self._body['content']['description'] if 'description' in self._body['content'] else None

    @description.setter
    def description(self, value):
        self._body['content']['description'] = value
        self._update_card()
        
    @property
    def collapse(self):
        """Whether the card is collapsed by default.

        :return: whether the card is collapsed by default
        :rtype: str"""
        return self._body['collapse']

    @collapse.setter
    def collapse(self, value):
        self._body['collapse'] = value
        self._update_card()

    @property
    def x_var(self):
        """The X variable for this card.

        :return: X variable for this card
        :rtype: str
        """
        return self._body['content']['x_var']

    @x_var.setter
    def x_var(self, val):
        self._body['content']['x_var'] = val
        self._update_card()

    @property
    def y_var(self):
        """The Y variable for this card.

        :return: Y variable for this card
        :rtype: str
        """
        return self._body['content']['y_var']

    @y_var.setter
    def y_var(self, val):
        self._body['content']['y_var'] = val
        self._update_card()

    @property
    def needs_guides(self):
        """Does this card need guides?

        :return: Whether this card needs guides
        :rtype: bool
        """
        return self._body['content']['needsGuides']

    @needs_guides.setter
    def needs_guides(self, var):
        self._body['content']['needsGuides'] = var
        self._update_card()

    @property
    def axis_labels(self):
        """The axis labels for this card

        :return: Axis labels for this card
        :rtype: TwoVariablePlot.XYMap
        """
        return TwoVariablePlot.XYMap(self, self._body['content']['axisLabels'])

    @axis_labels.setter
    def axis_labels(self, val):
        if isinstance(val, dict) and set(val.iterkeys()) == set(['x', 'y']):
            self._body['content']['axisLabels'] = val
        elif isinstance(val, TwoVariablePlot.XYMap):
            self._body['content']['axisLabels'] = { 'x': val.x, 'y': val.y }
        else:
            assert False, "axisLabels must specify 'x' and 'y' values, either as a map or from another similar object"
        self._update_card()

    @property
    def label_format(self):
        """The label format for this card

        :return: A dictionary mapping axis names to printf-style
                 format-string specifiers (for example, ".3s")
        :rtype: dict
        """
        return TwoVariablePlot.XYMap(self, self._body['content']['labelFormat'])

    @label_format.setter
    def label_format(self, val):
        if isinstance(val, dict) and set(val.iterkeys()) == set(['x', 'y']):
            self._body['content']['labelFormat'] = val
        elif isinstance(val, TwoVariablePlot.XYMap):
            self._body['content']['labelFormat'] = { 'x': val.x, 'y': val.y }
        else:
            assert False, "labelFormat must specify 'x' and 'y' values, either as a map or from another similar object"
        self._update_card()
        

        
