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

from two_variable_plot import TwoVariablePlot

class ScatterPlotCard(TwoVariablePlot):
    """Represents a scatter plot card on the server.

    :param DataSource datasource: The data source containing the data to be plotted.
    :param str x_var: The X-axis variable for the card's plot.
    :param str y_var: The Y-axis variable for the card's plot.
    :param str title: The title of the card.
    :param str description: A textual description of the card.
    :param bool needs_guides: Whether the card needs guides.
    :param XYMap axis_labels: Axis labels for this card's plot.  Set member fields "x" and "y" to set the X and Y axis labels.
    :param XYMap label_format: Label format for this card.  Set member fields "x" and "y" to set the X and Y axis printf-style format-strings; for example, ".3s".
    :param bool collapse: Whether the card should default to be collapsed.

    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.title: The title of the card
    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.x_var: The X-axis variable for the card's plot
    :var str ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.y_var: The Y-axis variable for the card's plot
    :var bool ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.needs_guides: Whether the card needs guides
    :var XYMap ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.axis_labels: Axis labels for this card's plot.  Set member fields "x" and "y" to set the X and Y axis labels.
    :var XYMap ~eureqa.analysis_cards.two_variable_plot.TwoVariablePlot.label_format: Label format for this card.  Set member fields "x" and "y" to set the X and Y axis printf-style format-strings; for example, ".3s".
    """
    _item_type = 'SCATTER_PLOT'
