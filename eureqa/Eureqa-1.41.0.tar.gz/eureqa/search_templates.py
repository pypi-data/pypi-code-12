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

from search_settings import SearchSettings


class SearchTemplates:
    """Provides a set of search settings for well known search scenarios.

    :param eureqa.Eureqa eureqa: A eureqa connection.
    """

    def __init__(self, eureqa):
        """For internal use only"""

        self._eureqa = eureqa

    def numeric(self, name, target_variable, input_variables):
        """The numeric search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :rtype: SearchSettings
        """
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % 'generic'
        args = {
            'search_name': name,
            'input_variables': [{"variable_name": v} for v in input_variables],
            'target_variable': target_variable
        }
        self._eureqa._session.report_progress('Creating numeric settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', args)
        settings = SearchSettings.from_json(body)
        return settings

    def classification(self, name, target_variable, input_variables):
        """The classification search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :rtype: SearchSettings
        """
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % 'classification'
        args = {
            'search_name': name,
            'input_variables': [{"variable_name": v} for v in input_variables],
            'target_variable': target_variable
        }
        self._eureqa._session.report_progress('Creating classification settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', args)
        settings = SearchSettings.from_json(body)
        return settings

    def time_series(self, name, target_variable, input_variables, min_delay=1, data_custom_history_fraction=0.1,
                    max_delays_per_variable=0):
        """The time series search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :param int min_delay: Optionally specify the minimum number of rows used in the range functions.
        :param float data_custom_history_fraction: Optionally specify the percentage of the data to be withheld
            from history blocks. Specifies the maximum possible delay for a history block.
        :param int max_delays_per_variable: Optionally overrides data_custom_history_fraction to directly set
            the maximum possible delay for a history block.
        :rtype: SearchSettings
        """
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % 'timeseries'
        args = {
            'search_name': name,
            'input_variables': [{"variable_name": v} for v in input_variables],
            'target_variable': target_variable,
            'default_min_delay': min_delay,
            'data_custom_history_fraction': data_custom_history_fraction,
            'max_delays_per_variable': max_delays_per_variable
        }
        self._eureqa._session.report_progress('Creating time series settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', args)
        settings = SearchSettings.from_json(body)
        return settings

    def time_series_classification(self, name, target_variable, input_variables, min_delay=1,
                                   data_custom_history_fraction=0.1, max_delays_per_variable=0):
        """The time series classification search settings template.

        :param str name: The search name.
        :param str target_variable: The target variable.
        :param list input_variables: The list (str) of input variables.
        :param int min_delay: Optionally specify the minimum number of rows used in the range functions.
        :param float data_custom_history_fraction: Optionally specify the percentage of the data to be withheld
            from history blocks. Specifies the maximum possible delay for a history block.
        :param int max_delays_per_variable: Optionally overrides data_custom_history_fraction to directly set
            the maximum possible delay for a history block.
        :rtype: SearchSettings
        """
        try: input_variables = list(input_variables) # make sure the input variables are a list
        except TypeError: raise Exception('Input variables must be a list.')

        endpoint = '/fxp/search_templates/%s/create_settings' % 'timeseries_classification'
        args = {
            'search_name': name,
            'input_variables': [{"variable_name": v} for v in input_variables],
            'target_variable': target_variable,
            'default_min_delay': min_delay,
            'data_custom_history_fraction': data_custom_history_fraction,
            'max_delays_per_variable': max_delays_per_variable
        }
        self._eureqa._session.report_progress('Creating time series classification settings for search: \'%s\'.' % name)
        body = self._eureqa._session.execute(endpoint, 'POST', args)
        settings = SearchSettings.from_json(body)
        return settings
