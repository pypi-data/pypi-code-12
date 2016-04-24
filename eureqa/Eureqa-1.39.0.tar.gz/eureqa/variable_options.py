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
import missing_value_policies


class VariableOptions:
    """Represents a set of settings for a variable that can be included into a search.

    :param str name: The name of the variable. It is the same as a column name in the list of data source columns.
    :param bool smoothing_enabled: Whether the smoothing capability is enabled or not
    :param int smoothing_along: The x variable used to apply smoothing.
    :param int smoothing_percent: The amount of smoothing to apply, where 0% indicates none and 100% indicates max smoothing.
    :param int smoothing_weight: A variable or expression which indicates the weights to apply to each row during smoothing.
    :param str missing_value_policy: A policy name for the processing of missing values. One of the values from missing_value_policies module can be used.
    :param bool remove_outliers_enabled: Enables removal of rows which contain outlier.
    :param float outlier_threshold: The threshold at which a point is considered an outlier and will be removed.
    :param bool normalize_enabled: Enables normalization of the variable.
    :param int normalization_offset: A constant offset to subtract from each value.
    :param int normalization_scale: A constant factor to divide each value by before adding the offset.

    :var str name: The name of the variable. It is the same as a column name in the list of data source columns.
    :var bool missing_values_enabled: Enables additional processing of missing values.
    :var str missing_value_policy: A policy name for the processing of missing values. One of the values from
        missing_value_policies module can be used. missing_value_policies.column_mean is used if the additional
        processing of missing values is enabled but no policy name provided.
    :var bool remove_outliers_enabled: Enables normalization of the variable.
    :var float outlier_threshold: The threshold at which a point is considered an outlier and will be removed.
    """

    def __init__(self, name=None, smoothing_enabled=False, smoothing_along=None, smoothing_percent=None,
                 smoothing_weight=None, missing_value_policy=missing_value_policies.column_iqm,
                 remove_outliers_enabled=False, outlier_threshold=None, normalize_enabled=False,
                 normalization_offset=None, normalization_scale=None):
        self.smoothing_enabled = smoothing_enabled

        if smoothing_enabled and smoothing_along is None:
            self.smoothing_along = '<row>'
        else:
            self.smoothing_along = smoothing_along

        if smoothing_enabled and smoothing_percent is None:
            self.smoothing_percent = 50
        else:
            self.smoothing_percent = smoothing_percent

        if smoothing_enabled and smoothing_weight is None:
            self.smoothing_weight = '<none>'
        else:
            self.smoothing_weight = smoothing_weight

        self.missing_value_policy = missing_value_policy

        self.remove_outliers_enabled = remove_outliers_enabled
        if remove_outliers_enabled and outlier_threshold is None:
            self.outlier_threshold = 2
        else:
            self.outlier_threshold = outlier_threshold

        self.normalize_enabled = normalize_enabled
        if normalize_enabled and normalization_offset is None:
            self.normalization_offset = '<none>'
        else:
            self.normalization_offset = normalization_offset

        if normalize_enabled and normalization_scale is None:
            self.normalization_scale = '<none>'
        else:
            self.normalization_scale = normalization_scale

        self.name = name

        self._filter_enabled = False
        self._filter_expression = None

    def _set_filter(self, filter_enabled, filter_expression):
        # It is more appropriate to expose filter properties as a search options, not variable options.
        # Therefore they are not exposed as public fields. But we have to keep them at this level
        # because that's what the backend expects.
        self._filter_enabled = filter_enabled
        self._filter_expression = filter_expression

    def _to_json(self):
        body = {'variable_name': self.name}

        if self.smoothing_along:
            body['smooth_enabled'] = True
            body['smooth_along'] = self.smoothing_along
            body['smooth_percent'] = self.smoothing_percent
            body['smooth_weight'] = self.smoothing_weight
        else:
            body['smooth_enabled'] = False

        if self._filter_expression:
            body['filter_enabled'] = True
            body['filter_expression'] = self._filter_expression
        else:
            body['filter_enabled'] = False

        if self.missing_value_policy:
            body['missing_value_policy'] = self.missing_value_policy

        if self.outlier_threshold:
            body['remove_outliers_enabled'] = True
            body['outlier_threshold'] = self.outlier_threshold
        else:
            body['remove_outliers_enabled'] = False

        if self.normalization_offset:
            body['normalize_enabled'] = True
            body['normalize_offset'] = self.normalization_offset
            body['normalize_scale'] = self.normalization_scale
        else:
            body['normalize_enabled'] = False
        return body

    def _from_json(self, body):
        self.name = body['variable_name']
        self.smoothing_enabled = body['smooth_enabled']
        self.smoothing_along = body.get('smooth_along')
        self.smoothing_percent = body.get('smooth_percent')
        self.smoothing_weight = body.get('smooth_weight')
        self.missing_value_policy = body.get('missing_value_policy')
        self.remove_outliers_enabled = body['remove_outliers_enabled']
        self.outlier_threshold = body.get('outlier_threshold')
        self.normalize_enabled = body['normalize_enabled']
        self.normalization_offset = body.get('normalize_offset')
        self.normalization_scale = body.get('normalize_scale')
        self._filter_enabled = body['filter_enabled']
        self._filter_expression = body.get('filter_expression')
        self._body = body

    @classmethod
    def from_json(cls, body):
        variableOptions = VariableOptions()
        variableOptions._from_json(body)
        return variableOptions

    def __eq__(self, other):
        if not isinstance(other, VariableOptions):
            return False
        return (self.name == other.name and self.smoothing_enabled == other.smoothing_enabled
                and self.smoothing_along == other.smoothing_along
                and self.smoothing_percent == other.smoothing_percent
                and self.smoothing_weight == other.smoothing_weight
                and self.missing_value_policy == other.missing_value_policy
                and self.remove_outliers_enabled == other.remove_outliers_enabled
                and self.outlier_threshold == other.outlier_threshold
                and self.normalize_enabled == other.normalize_enabled
                and self.normalization_offset == other.normalization_offset
                and self.normalization_scale == other.normalization_scale
                and self._filter_enabled == other._filter_enabled
                and self._filter_expression == other._filter_expression)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        tpl = (self.smoothing_enabled, self.smoothing_along, self.smoothing_percent, self.smoothing_weight,
               self.missing_value_policy, self.remove_outliers_enabled,
               self.outlier_threshold, self.normalize_enabled, self.normalization_offset, self.normalization_scale,
               self._filter_enabled, self._filter_expression, self.name)
        return hash(tpl)

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)


def _from_json(body):
    option = VariableOptions()
    option._from_json(body)
    return option
