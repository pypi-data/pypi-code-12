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


import json

class VariableDetails:
    """Represents a variable_details object on the server.

    :param DataSource data_source: The data source definition for the variables. 
    :param dict body: Class metadata as dictionary

    :var str `~eureqa.variable.VariableDetails.name`: The name of the variable.
    :var str `~eureqa.variable.VariableDetails.display_name`: The name to display in the ui`.
    :var str `~eureqa.variable.VariableDetails.expression`: The expression used to create the variable if it is a custom variable
    :var int `~eureqa.variable.VariableDetails.min_value`: The smallest value.
    :var int `~eureqa.variable.VariableDetails.max_value`: The largest value.
    :var int `~eureqa.variable.VariableDetails.mean_values`: The mean value.
    :var int `~eureqa.variable.VariableDetails.standard_deviation`: The standard deviation of the values.
    :var int `~eureqa.variable.VariableDetails.distinct_values`: The number of distinct values.
    :var int `~eureqa.variable.VariableDetails.missing_values`: The number of missing values.
    :var str `~eureqa.variable.VariableDetails.error_metric`: One of the error metrics from :mod:`eureqa.error_metric`.
    :var str `~eureqa.variable.VariableDetails.datatype`: Whether it is a boolean or numeric variable
    :var int `~eureqa.variable.VariableDetails.num_zeros`: The number of zero values.
    :var int `~eureqa.variable.VariableDetails.num_ones`: The number of one values if it is a boolean variable.
    :var list `~eureqa.variable.VariableDetails.categories`: The categories.
    :var `~eureqa.DataSource` `~eureqa.variable.VariableDetails.data_source`: The DataSource the VariableDetails belongs to
    """

    def __init__(self, body, data_source):
        """For internal use only"""

        self._id = body['variable_id']
        self.name = body['variable_name']
        self.display_name = body.get('display_name')
        self.expression = body.get('expression')
        self.min_value = body['min_value']
        self.max_value = body['max_value']
        self.mean_value = body['mean_value']
        self.standard_deviation = body['standard_deviation']
        self.distinct_values = body['distinct_values']
        self.missing_values = body['missing_values']
        self.num_zeroes = body['num_zeros']
        self.total_rows = body['total_rows']
        self.datatype = body['datatype']
        self.num_ones = body.get('num_ones')
        self.categories = body.get('categories')
        self.data_source = data_source
        self._body = body

    def _to_json(self):
        body = {
            'variable_id' : self._id,
            'variable_name' : self.name,
            'display_name' : self.display_name,
            'expression' : self.expression,
            'min_value' : self.min_value,
            'max_value' : self.max_value,
            'mean_value' : self.mean_value,
            'standard_deviation' : self.standard_deviation,
            'distinct_values' : self.distinct_values,
            'missing_values' : self.missing_values,
            'num_zeros' : self.num_zeroes,
            'total_rows' : self.total_rows,
            'datatype' : self.datatype,
            'num_ones' : self.num_ones,
            'categories' : self.categories,
            'datasource_id' : self.data_source._data_source_id,
        }
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)
        
    def update_display_name(self, display_name):
        """Update the display name of the variable

        :param str display_name:
            The name to show for the variable in the ui
        """
        body = {
            'variable_id' : self._id,
            'variable_name' : self.name,
            'display_name' : display_name,
            'datasource_id' : self.data_source._data_source_id
        }
        endpoint = '/fxp/datasources/%s/variables/%s' % (self.data_source._data_source_id, self._id)
        result = self.data_source._eureqa._session.execute(endpoint, 'PUT', body)
        self.__dict__ = self.data_source.get_variable(self.name).__dict__
        

    def update_categories(self, categories):
        """Update the display name of the variable

        :param list categories:
            The categories to set for the variable
        """
        body = {
            'variable_id' : self._id,
            'variable_name' : self.name,
            'categories' : categories,
            'datasource_id' : self.data_source._data_source_id
        }
        endpoint = '/fxp/datasources/%s/variables/%s' % (self.data_source._data_source_id, self._id)
        result = self.data_source._eureqa._session.execute(endpoint, 'PUT', body)
        self.__dict__ = self.data_source.get_variable(self.name).__dict__

class Variable(VariableDetails):
    def __init__(*args, **kwargs):
        warnings.warn("Class 'Variable' has been renamed to 'VariableOptions'", DeprecationWarning)
        super(Variable, self).__init__(*args, **kwargs)
