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

from search import Search
from variable_details import VariableDetails
from utils import *

from session import Http404Exception

import base64
import json
import urllib

import warnings

class DataSource:
    """Represents an interface to a data source on the server

    :param Eureqa eureqa: A eureqa connection.
    :param dict body: Class metadata as dictionary.

    :var str `~eureqa.data_source.DataSource.name`: The data source name.
    :var int `~eureqa.data_source.DataSource.number_columns`: The number of columns in the data source.
    :var int `~eureqa.data_source.DataSource.number_rows`: The number of rows (variables) in the data source.
    """

    def __init__(self, eureqa, body):
        """For internal use only
        """

        self._eureqa = eureqa
        self._data_source_id = body['datasource_id']
        self.name = body['datasource_name']
        self._number_columns = int(body.get('column_count', '0'))
        self._number_rows = int(body.get('row_count', '0'))
        self._data_file_name = body.get('file_name', '')
        self._data_file_size = int(body.get('file_size', '0'))
        self._data_file_uploaded_user = body.get('file_uploaded_user', '')
        self._data_file_uploaded_date = int(body.get('file_uploaded_date', '0'))
        self._data_file_objstore_uri = body.get('file_objstore_uri', '')
        self._body = body

    @property
    def number_columns(self):
        return self._number_columns

    @property
    def number_rows(self):
        return self._number_rows

    def _to_json(self):
        body = {
            'name': self.name,
            'number_columns': self.number_columns,
            'number_rows': self.number_rows
        }
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    def delete(self):
        """Deletes the data source from the server.
        
        :raise Exception: If the data source is already deleted.
        """
        self._eureqa._session.report_progress('Deleting datasource: \'%s\'.' % self.name)
        self._eureqa._session.execute('/fxp/datasources/%s' % self._data_source_id, 'DELETE')

    def download_data_file(self, file_path):
        """Downloads the originally uploaded data file from the server.

        :param str file_path: the filepath at which to save the data

        """
        if not self._data_file_objstore_uri: raise Exception("Datasource %s is too old. The original data can only be retrieved from datasources made with newer versions of Eureqa" % (self.name))
        result = self._eureqa._session.execute(self._data_file_objstore_uri, 'GET', raw_returnfile=file_path)

    def get_variables(self):
        """Retrieves from the server a list of variables in a data set.
        
        :return:
            A list of the same variables as visible in Eureqa UI.
            Including all derived variables.
        :rtype: list of str
        """
        endpoint = '/fxp/datasources/%s/variables' % self._data_source_id
        self._eureqa._session.report_progress('Getting variable details for datasource: \'%s\'.' % self.name)
        body = self._eureqa._session.execute(endpoint, 'GET')
        return [x['variable_name'] for x in body]

    def get_searches(self):
        """Retrieves from the server a list of searches associated with the data source.

        :return: The list of all searches associated with the data source.
        :rtype: list of :class:`~eureqa.Search`
        """

        endpoint = '/fxp/datasources/%s/searches' % self._data_source_id
        self._eureqa._session.report_progress('Getting searches for datasource: \'%s\'.' % self.name)
        body = self._eureqa._session.execute(endpoint, 'GET')
        return [Search(x, self._eureqa) for x in body]

    def create_search(self, search_settings, _hidden = False):
        """Creates a new search with input as a SearchSettings object.

        :param `~eureqa.SearchSettings` search_settings: the settings for creating a new search.
        :return: A Search object which represents a newly create search on the server.
        :rtype: ~eureqa.Search
        """

        endpoint = "/fxp/datasources/%s/searches" % self._data_source_id
        body = search_settings._to_json()
        body['hidden'] = _hidden
        self._eureqa._session.report_progress('Creating search for datasource: \'%s\'.' % self.name)
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        search_id = result['search_id']
        return self._eureqa._get_search_by_search_id(self._data_source_id, search_id)

    def evaluate_expression(self, expressions, _data_split='all'):
        warnings.warn("This function has been deprecated.  Please use `Eureqa.evaluate_expression()` instead.", DeprecationWarning)
        return self._eureqa.evaluate_expression(self, expressions, _data_split=_data_split)

    def create_variable(self, expression, variable_name):
        """Adds a new variable to the data_source with values from evaluating the given expression.

        :param str expression: the expression to evaluate to fill in the values
        :param str variable_name: what to name the new variable
        """
        endpoint = '/fxp/datasources/%s/variables' % self._data_source_id
        body = {'datasource_id': self._data_source_id,
                'expression': expression,
                'variable_name': variable_name}
        result = self._eureqa._session.execute(endpoint, 'POST', body)
        self.__dict__ = self._eureqa.get_data_source_by_id(self._data_source_id).__dict__
        
    def get_variable_details(self, variable_name):
        """Retrieves the details for the requested variable from the data_source.
        
        :param str variable_name: the name of the variable to get the details for
        :return:
            The object representing the variable details
        :rtype: VariableDetails
        """
        endpoint = '/fxp/datasources/%s/variables/%s' % (self._data_source_id, urllib.quote_plus(base64.b64encode('%s-_-%s' % (self._data_source_id, variable_name))))
        self._eureqa._session.report_progress('Getting variable details for datasource: \'%s\'.' % self.name)
        body = self._eureqa._session.execute(endpoint, 'GET')
        return VariableDetails(body, self)

    def get_variable(self, variable_name):
        warnings.warn("'get_variable()' function deprecated; please call as 'get_variable_details()' instead", DeprecationWarning)
        return self.get_variable_details(variable_name)
