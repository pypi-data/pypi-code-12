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

from eureqa.analysis.components.base import _Component
from eureqa.utils.jsonrest import _JsonREST

class VariableLineGraph(_Component):
    """
    Represents a variable line graph on the server.

    :param eureqa.DataSource datasource: Data source for the component's data
    :param str x_var: Name of the variable to plot as the X axis
    :param str plotted_vars: List of string-names of variables to plot.
    :param str focus_variable: Name of the variable in 'plotted_vars' to bring to the foreground
    :param bool should_center: Should the plot be centered?
    :param bool should_scale: Should the plot scale?
    :param bool collapse: Whether the component should default to be collapsed.

    :var str title: The component's title.
    :var str focus_variable: Focused (foreground) variable for the component.  Must be a member of ~eureqa.analysis.components.ByRowPlot.plotted_variables
    :var str x_var: Name of the variable to plot as the X axis
    :var list plotted_variables: Variables to plot.  (List of string variable names.)
    :var bool should_center: Should the plot be centered?
    :var bool should_scale: Should the plot scale?
    """

    _component_type_str = 'VARIABLE_LINE_GRAPH'

    def __init__(self, datasource=None, x_var=None, plotted_variables=None, focus_variable=None, should_center=None,
                 should_scale=None, analysis=None, component_id=None, component_type=None):
        # Set 'self._options' first; property setters used below populate it
        self._options = {}

        if datasource is not None:
            self.datasource = datasource

        if x_var is not None:
            self.x_var = x_var

        if plotted_variables is not None:
            self.plotted_variables = plotted_variables

        if focus_variable is not None:
            self.focus_variable = focus_variable

        if should_center is not None:
            self.should_center = should_center

        if should_scale is not None:
            self.should_scale = should_scale

        super(VariableLineGraph, self).__init__(analysis=analysis, component_id=component_id, component_type=component_type)

    @property
    def datasource(self):
        """The data source providing data for this component

        :return: data source providing data for this component
        """
        return getattr(self, "_datasource", None)

    @datasource.setter
    def datasource(self, val):
        self._datasource = val
        self._datasource_id = val._data_source_id
        self._update()


    @property
    def focus_variable(self):
        """The variable that is currently in focus (in the foreground) for this component.
        Must be a member of 'plotted_variables'.

        :return: focus_variable for this component
        :rtype: str
        """

        return self._options.get('focusVariable')

    @focus_variable.setter
    def focus_variable(self, val):
        self._options['focusVariable'] = val
        self._update()

    @property
    def x_var(self):
        """The X-axis variable for this component

        :return: the name of the X-axis variable for this component
        :rtype: str
        """

        return self._options.get('xAxisVariable')

    @x_var.setter
    def x_var(self, val):
        self._options['xAxisVariable'] = val
        self._update()

    @property
    def plotted_variables(self):
        """The plotted variables for this component.

        :return: List of the names of the variables being plotted against the X axis
        :rtype: tuple
        """
        return self._options.get('plottedVariables')

    @plotted_variables.setter
    def plotted_variables(self, val):
        self._options['plottedVariables'] = val
        self._update()

    @property
    def should_center(self):
        """The should_center option for this component.

        :return: whether this plot should be centered
        :rtype: bool
        """

        return self._options.get('shouldCenter')

    @should_center.setter
    def should_center(self, val):
        self._options['shouldCenter'] = val
        self._update()

    @property
    def should_scale(self):
        """The should_scale option for this component.

        :return: whether this plot should be scaled
        :rtype: bool
        """
        return self._options.get('shouldScale')

    @should_scale.setter
    def should_scale(self, val):
        self._options['shouldScale'] = val
        self._update()


    def _fields(self):
        return super(VariableLineGraph, self)._fields() + [ 'datasource_id', 'options' ]

