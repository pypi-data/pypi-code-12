# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from collections import defaultdict
from copy import deepcopy
from itertools import groupby

import re
from dateutil.parser import parse
from django.core.exceptions import ImproperlyConfigured

from django.utils import six

from elasticsearch_dsl.filter import F
from elasticsearch_dsl.query import FunctionScore

from rest_framework import filters
from rest_framework.exceptions import ParseError
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings

from ..filters import FilterOptionsMixin


def _function_score_params(origin_parser=None, offset_parser=None, scale_parser=None, decay_parser=None, global_disallowed=None):
    global_disallowed = global_disallowed or []
    parsers = {"origin": origin_parser or (lambda values, value: value),
               "offset": offset_parser or (lambda values, value: value),
               "scale": scale_parser or (lambda values, value: value),
               "decay": decay_parser or (lambda values, value: float(value) if value else None)}

    def wrapper(base_param, defaults=None, disallowed=None):
        disallowed = global_disallowed + (disallowed or [])
        defaults = defaults or {}
        params = {"origin": base_param,
                  "offset": "{}.offset".format(base_param),
                  "scale": "{}.scale".format(base_param),
                  "decay": "{}.decay".format(base_param)}

        def get_kwargs(request, view):
            if params["origin"] not in request.query_params and "origin" not in defaults:
                # origin has to be given via request or defaults
                return

            values = {"origin": request.query_params.get(params["origin"]) if "origin" not in disallowed else None,
                      "offset": request.query_params.get(params["offset"]) if "offset" not in disallowed else None,
                      "scale": request.query_params.get(params["scale"]) if "scale" not in disallowed else None,
                      "decay": request.query_params.get(params["decay"]) if "decay" not in disallowed else None}

            overrides = {}
            for arg, param in params.items():
                try:
                    val = parsers[arg](values, values[arg])
                    if isinstance(val, Exception):
                        raise val
                    if val is None:
                        continue
                    overrides.update({arg: val})
                except (ValueError, IndexError):
                    raise ParseError("Invalid value for '{}'".format(param))

            result = deepcopy(defaults)
            result.update(overrides)
            return result

        return get_kwargs
    return wrapper


class SearchMixin(object):

    search_param = getattr(api_settings, 'SEARCH_PARAM')

    def get_search(self, request):
        return request.query_params.get(self.search_param, "").strip()


class QueryParamFilterBuilderMixin(object):

    use_canonicals = True
    # List valid url operator
    valid_operators = []
    # Maps url operators to actual operator to use in the filter
    real_operators = {}
    # Fields used to store the value to match (should be exclusive of each other)
    value_operators = []
    # Operator negating the filter (should be one of value operator)
    negation_operators = []

    def get_fields(self, view):
        raise NotImplementedError("Subclass must implement 'get_fields'")

    def get_valid_fields(self, fields, include_canonicals=True):
        return (fields if include_canonicals else []) + ['{}.{}'.format(v, r) for v in fields for r in self.valid_operators]

    def get_operator(self, operator):
        return self.real_operators.get(operator, operator)

    def map_field(self, request, view, field):
        return field

    def map_value(self, request, view, field, operator, value):
        return value

    def parse_value(self, request, view, field, operator, value):
        return self.map_value(request, view, field, operator, value)

    def build_filter(self, field, **params):
        raise NotImplementedError("Subclass must implement 'build_filter'")

    def parse_param(self, param_name):
        parts = param_name.split('.')
        if parts[-1] in self.valid_operators:
            return '.'.join(parts[0:-1]), parts[-1]
        else:
            return param_name, None

    def get_mapped_params(self, request, view, valid_params):
        for param_name, param_value in valid_params:
            field, operator = self.parse_param(param_name)
            field = self.map_field(request, view, field)
            yield '.'.join(filter(None, [field, operator])), param_value

    def get_filter_params(self, request, view):
        valid_fields = self.get_valid_fields(self.get_fields(view), include_canonicals=self.use_canonicals)
        valid_params = list((k, v) for k, v in request.query_params.items() if k in valid_fields)
        clean_params = self.get_mapped_params(request, view, valid_params)
        field_groups = groupby(clean_params, key=lambda item: self.parse_param(item[0])[0])
        field_params = defaultdict(dict)
        for field, group in field_groups:
            for k, v in group:
                try:
                    field, operator = self.parse_param(k)
                except ValueError:
                    field, operator = k, None
                op = self.get_operator(operator)
                if op and op not in self.negation_operators:
                    field_params[field][op] = self.parse_value(request, view, field, op, v)
                else:
                    if op in self.negation_operators:
                        field_params[field]["negate"] = True
                    field_params[field][field] = self.parse_value(request, view, field, op, v)
        return field_params

    def get_filters(self, filter_params):
        filters = []
        for field, params in filter_params.items():
            negate = params.pop("negate", False)
            if self.value_operators and field not in params:
                raise ParseError("No value to match for '{}'".format(field))
            f = self.build_filter(field, **params)
            filters.append(~f if negate else f)
        return filters

    def filter_queryset(self, request, queryset, view):
        for filter in self.get_filters(self.get_filter_params(request, view)):
            queryset = queryset.filter(filter)
        return queryset


class BaseSearchFilterBackend(SearchMixin, FilterOptionsMixin, BaseFilterBackend):

    @property
    def search_type(self):
        raise NotImplementedError()

    def filter_queryset(self, request, queryset, view):
        search = self.get_search(request)
        if search:
            return queryset.query({self.search_type: dict(query=search, **self.get_options(view))})
        return queryset


class SimpleQueryStringFilter(BaseSearchFilterBackend):
    """
    Filter adding a simple query string to a search

    For the available view options, see:
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-simple-query-string-query.html

    Example::

        class YourView(APIView):

            simple_query_string_filter_options = {
                "analyzer": "snowball",
                "fields": ["body^5", "_all"],
                "default_operator": "and"
            }

    Note: Make sure to add _score to your default ordering if you want results sorted by relevance

    """
    search_type = "simple_query_string"


class MultiMatchFilter(BaseSearchFilterBackend):
    """
    Filter adding a multi match to a search

    For the available view options, see:
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html

    Example::

        class YourView(APIView):

            multi_match_options = {
                "type": "best_fields",
                "fields": ["subject", "message"],
                "tie_breaker": 0.3
            }

    Note: Make sure to add _score to your default ordering if you want results sorted by relevance

    """
    search_type = "multi_match"


class FunctionScoreFilter(FilterOptionsMixin, BaseFilterBackend):
    """
    Filter adding a function score to a search

    For the available view options, see:
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html

    Example::

        class YourView(APIView):

            function_score_options = {
                "functions": [
                    {
                        "field": "geo_point",
                        "function": "gauss",
                        "kwargs": FunctionScoreFilter.geo_params("nearby", {"offset": "1km", "scale": "1km"}, disallowed=["decay"]),
                    }
                ]
            }

    kwargs can either take a dictionary, or a callable(request, view) returning a dictionary.
    The score function is ignored if the callable returns None. The request is malformed if the callable raises a ParseError

    Available param function shortcuts:

    * geo_params(param, defaults, disallowed) (e.g. &param=-36.8471855,174.7700463&param.offset=2km&param.scale=500m)
    * number_params(param, defaults, disallowed) (e.g. &param=10&param.offset=5&param.scale=2)
    * price_params(param) (e.g. &param=5)

    Note: Make sure to add _score to your default ordering if you want results sorted by relevance

    """
    geo_params = staticmethod(_function_score_params(origin_parser=lambda values, value: dict(zip(('lat', 'lon'), map(lambda v: float(v.strip()), value.split(',', 1)))),
                                                     offset_parser=lambda values, value: value if value is None or re.match("\d+[kc]?m", value) else ValueError(),
                                                     scale_parser=lambda values, value: value if value is None or re.match("\d+[kc]?m", value) else ValueError()))

    date_params = staticmethod(_function_score_params(origin_parser=lambda values, value: value,
                                                     offset_parser=lambda values, value: value if value is None or re.match("\d+d", value) else ValueError(),
                                                     scale_parser=lambda values, value: value if value is None or re.match("\d+d", value) else ValueError()))

    number_params = staticmethod(_function_score_params(origin_parser=lambda values, value: float(value),
                                                       offset_parser=lambda values, value: float(value),
                                                       scale_parser=lambda values, value: float(value)))

    price_params = staticmethod(_function_score_params(origin_parser=lambda values, value: float(value) / 2,
                                                       offset_parser=lambda values, value: float(values['origin']) / 2,
                                                       scale_parser=lambda values, value: float(values['origin']) / 3,
                                                       global_disallowed=['offset', 'scale', 'decay']))

    def get_functions(self, request, view):
        functions = []
        for f in self.get_option(view, "functions"):
                kwargs = f.get('kwargs')
                if callable(kwargs):
                    kwargs = kwargs(request, view)
                if not kwargs:
                    continue
                function = {f.get("function"): {f.get("field"): kwargs}}
                if f.get("weight", False):
                    function.update({'weight': f.get("weight")})
                functions.append(function)
        return functions

    def filter_queryset(self, request, queryset, view):
        functions = self.get_functions(request, view)
        if functions:
            params = {k: v for k, v in self.get_options(view).items() if k not in ['functions']}
            return queryset.query(FunctionScore(functions=functions, **params))
        return queryset


class TermFilter(BaseFilterBackend):

    def get_valid_terms_filters(self, view):
        filters = getattr(view, 'term_filters', [])
        if isinstance(filters, six.string_types):
            return (filters,)
        return filters

    def get_term_filters(self, request, valid_filters):
        return {k: v.strip() for k, v in request.query_params.items() if k in valid_filters}

    def filter_queryset(self, request, queryset, view):
        valid_filters = self.get_valid_terms_filters(view)

        term_filters = self.get_term_filters(request, valid_filters)

        for field, values in term_filters.items():
            queryset = queryset.filter("term", **{field: values})

        return queryset


class TermsFilter(QueryParamFilterBuilderMixin, FilterOptionsMixin, BaseFilterBackend):

    EQUAL = 'eq'
    NOT_EQUAL = 'neq'
    EXECUTION = 'op'

    valid_operators = [NOT_EQUAL, EXECUTION]
    real_operators = {EXECUTION: 'execution'}
    value_operators = [EQUAL, NOT_EQUAL]
    negation_operators = [NOT_EQUAL]

    real_operators_value_map = {
        'execution': {'any': 'plain', 'all': 'and'}
    }

    separator = getattr(api_settings, 'PARAM_VALUES_SEPARATOR', ',')

    def get_fields(self, view):
        return getattr(view, 'terms_filters', []) + self.get_option(view, 'fields', []) + list(self.get_option(view, 'field_map', {}).keys())

    def map_field(self, request, view, field):
        return self.get_option(view, 'field_map', {}).get(field, field)

    def map_value(self, request, view, field, operator, value):
        value_map = self.get_option(view, 'value_map', {})
        if field not in value_map:
            return value
        try:
            return value_map[field][value]
        except KeyError:
            raise ParseError("Invalid value for '{}'".format(field))

    def parse_value(self, request, view, field, operator, value):
        if operator in self.real_operators.values():
            try:
                return self.real_operators_value_map[operator][value]
            except KeyError:
                rev_op = dict((v, k) for k, v in self.real_operators.items())
                raise ParseError("Invalid value for modifier '{}'".format(rev_op.get(operator)))
        return [self.map_value(request, view, field, operator, i.strip()) for i in value.split(self.separator)]

    def build_filter(self, field, **params):
        return F("terms", **params)


class IndexedGeoShapeFilter(FilterOptionsMixin, BaseFilterBackend):

    def get_valid_params(self, view):
        return self.get_options(view).keys()

    def get_params(self, request, view):
        valid_params = self.get_valid_params(view)
        return {k: v for k, v in request.query_params.items() if k in valid_params}

    def get_filters(self, request, view):
        params = self.get_params(request, view)
        options = self.get_options(view)
        filters = []
        for param, value in params.iteritems():
            field_config = options.get(param)
            for id in value.split(','):
                filter_config = deepcopy(field_config['config'])
                field = field_config.get('field') if 'field' in field_config else param
                cache = field_config.get('cache') if 'cache' in field_config else False
                filter_config['indexed_shape']['id'] = id
                filters.append(F("geo_shape", **{field: filter_config, '_cache': cache}))
        return filters

    def filter_queryset(self, request, queryset, view):
        filters = self.get_filters(request, view)
        if filters:
            return queryset.filter("bool", must=[F("bool", should=filters)])
        return queryset


class MoreLikeThisFilter(FilterOptionsMixin, BaseFilterBackend):

    separator = getattr(api_settings, 'PARAM_VALUES_SEPARATOR', ',')
    LIKE_PARAM = getattr(api_settings, 'LIKE_PARAM', 'like')

    def get_like_ids(self, request):
        like_params = request.query_params.get(self.LIKE_PARAM)
        if like_params:
            return set([param.strip() for param in like_params.split(',')])
        return None

    def filter_queryset(self, request, queryset, view):

        like_params = self.get_like_ids(request)

        if like_params:

            options = self.get_options(view)

            docs = [
                {
                    "_type": options.get('type'),
                    "_id": id
                } for id in like_params
            ]

            queryset = queryset.query("more_like_this", fields=options.get('fields'), docs=docs,
                                      min_term_freq=options.get('min_term_freq'), max_query_terms=options.get('max_query_terms'))

        return queryset


class GeoDistanceFilter(FilterOptionsMixin, BaseFilterBackend):

    def get_valid_params(self, view):
        return self.get_option(view, 'fields', []) + list(self.get_option(view, 'field_map', {}).keys())

    def map_param_name(self, view, param_name):
        return self.get_option(view, 'field_map', {}).get(param_name, param_name)

    def parse_param_value(self, view, param_name, param_value):

        try:
            values = []
            for value in param_value.split(' '):
                matches = re.match(r'(\d+(mm|cm|m|km|in|yd|ft|mi|nmi))@([\-\+]?\d+(\.\d+)?),([\-\+]?\d+(\.\d+)?)', value)
                values.append((matches.group(1),) + (map(float, matches.group(5, 3)),))
            return values
        except:
            raise ParseError("Invalid distance for '{}'".format(param_name))

    def get_filters(self, request, view):
        valid_params = self.get_valid_params(view)
        params = {self.map_param_name(view, k): self.parse_param_value(view, k, v) for k, v in request.query_params.items() if k in valid_params}
        filters = []

        for field, values in params.items():
            for config in values:
                filters.append(F("geo_distance", **{field: config[1], 'distance': config[0]}))
        return filters

    def filter_queryset(self, request, queryset, view):
        filters = self.get_filters(request, view)
        if filters:
            return queryset.filter("bool", must=[F("bool", should=filters)])
        return queryset


class CannedTermsFilter(BaseFilterBackend):

    def get_valid_terms_filters(self, view):
        return getattr(view, 'canned_terms_filters', {})

    def get_terms_filters(self, request, valid_filters):
        return {valid_filters[k]['field']: valid_filters[k]['values'] for k, v in request.query_params.items() if k in valid_filters.keys() and bool(v)}

    def filter_queryset(self, request, queryset, view):
        valid_filters = self.get_valid_terms_filters(view)

        terms_filters = self.get_terms_filters(request, valid_filters)

        for field, values in terms_filters.items():
            queryset = queryset.filter("terms", **{field: values})

        return queryset


class IdsFilter(FilterOptionsMixin, BaseFilterBackend):

    separator = getattr(api_settings, 'PARAM_VALUES_SEPARATOR', ',')
    IDS_PARAM = getattr(api_settings, 'IDS_PARAM', 'id')

    def get_ids(self, view, request):
        type = self.get_option(view, 'type', None)
        id_params = request.query_params.get(self.IDS_PARAM)
        if id_params:
            return type, set([param.strip() for param in id_params.split(',')])
        return None, None

    def filter_queryset(self, request, queryset, view):
        type, ids = self.get_ids(view, request)
        if ids:
            return queryset.filter("ids", type=type, values=list(ids))
        return queryset


class MatchQueryFilter(BaseFilterBackend):

    def get_params(self, view):
        filters = getattr(view, 'match_query_filters', [])
        if isinstance(filters, six.string_types):
            return (filters,)
        return filters

    def get_match_query_filters(self, request, valid_filters):
        return {k: v.strip() for k, v in request.query_params.items() if k in valid_filters}

    def filter_queryset(self, request, queryset, view):
        valid_filters = self.get_params(view)

        query_filters = self.get_match_query_filters(request, valid_filters)

        for field, value in query_filters.items():
            queryset = queryset.filter("query", match={field: value})

        return queryset


class MatchQueriesFilter(BaseFilterBackend):

    separator = getattr(api_settings, 'PARAM_VALUES_SEPARATOR', ',')

    def get_params(self, view):
        filters = getattr(view, 'match_queries_filters', [])
        if isinstance(filters, six.string_types):
            return (filters,)
        return filters

    def get_match_queries_filters(self, request, valid_filters):
        return {k: [i.strip() for i in v.split(self.separator)] for k, v in request.query_params.items() if k in valid_filters}

    def filter_queryset(self, request, queryset, view):
        valid_filters = self.get_params(view)

        query_filters = self.get_match_queries_filters(request, valid_filters)

        should = None
        for field, values in query_filters.items():
            for value in values:
                if should is None:
                    should = F("query", match={field: value})
                else:
                    should |= F("query", match={field: value})
        if should:
            return queryset.filter("bool", must=F("bool", should))

        return queryset


class NumericRangeFilter(FilterOptionsMixin, BaseFilterBackend):

    GREATER_THAN = 'gt'
    GREATER_THAN_OR_EQUAL = 'gte'
    LESS_THAN = 'lt'
    LESS_THAN_OR_EQUAL = 'lte'
    TIME_ZONE = 'time_zone'
    TZ = 'tz'

    TIMEZONE_OPERATORS = [TIME_ZONE, TZ]

    OPERATOR_SYNONYMS = {
       TZ: TIME_ZONE,
    }

    VALID_SUFFIXES = [GREATER_THAN, GREATER_THAN_OR_EQUAL, LESS_THAN, LESS_THAN_OR_EQUAL, TIME_ZONE] + list(OPERATOR_SYNONYMS.keys())

    def get_valid_filters(self, view):
        filters = self.get_option(view, 'fields', []) + list(self.field_map.keys())
        if isinstance(filters, six.string_types):
            filters = (filters,)
        return ['{}.{}'.format(v, r) for v in filters for r in self.VALID_SUFFIXES]

    def get_range_query_filters(self, request, valid_filters):
        queries = defaultdict(dict)
        for k, v in ((k, v) for k, v in request.query_params.items() if k in valid_filters):
            field, operator = k.split('.')
            if operator not in self.TIMEZONE_OPERATORS:
                self.validate_field_value(field, v)
            if field in self.field_map:
                field = self.field_map[field]
            if operator in self.OPERATOR_SYNONYMS:
                operator = self.OPERATOR_SYNONYMS[operator]
            queries[field].update({operator: v})
        return queries

    def validate_field_value(self, field, value):
        validators = self.field_validators.get(field, [])
        for validator in validators:
            if validator == 'numeric':
                try:
                    float(value)
                except (ValueError, TypeError):
                    raise ParseError("Invalid numeric value for '{}'".format(field))
            elif validator == 'date':
                try:
                    if " " in value:
                        raise ParseError("Invalid date value for '{}', is your date in iso format and properly urlencoded?".format(field))
                    parse(value)
                except (ValueError, TypeError):
                    raise ParseError("Invalid date value for '{}'".format(field))
            elif callable(validator):
                validator(value)

    def filter_queryset(self, request, queryset, view):
        self.field_map = self.get_option(view, 'field_map', {})
        self.field_validators = self.get_option(view, 'field_validators', {})
        valid_filters = self.get_valid_filters(view)
        query_filters = self.get_range_query_filters(request, valid_filters)
        for field, params in query_filters.items():
            queryset = queryset.filter("range", **{field: params})
        return queryset


class NumericBinFilter(FilterOptionsMixin, BaseFilterBackend):
    """
    Allow to filter by numeric range using a named bin

    Example::

        numeric_bin_filter_options = {
            "rank_level": {
                "1": {"rank": {"gte": 0, "lte": 20}},
                "2": {"rank": {"gte": 21, "lte": 40}},
                "3": {"rank": {"gte": 41, "lte": 60}},
                "4": {"rank": {"gte": 61, "lte": 80}},
                "5": {"rank": {"gte": 81, "lte": 100}},
            }
        }
    """

    def filter_queryset(self, request, queryset, view):
        bins = self.get_options(view)
        filters = []
        for bin_name, bin_options in bins.items():
            if bin_name in request.query_params:
                options = [v.strip() for v in request.query_params.get(bin_name).split(',')]
                for o in options:
                    try:
                        filters.append(F("range", **bin_options[o]))
                    except KeyError:
                        raise ParseError("Invalid value '{}' for '{}'".format(o, bin_name))
        if filters:
            return queryset.filter("bool", must=[F("bool", should=filters)])
        return queryset


class ExistsFilter(BaseFilterBackend):

    fields_param = getattr(api_settings, 'EXISTS_PARAM', 'exists')

    def get_fields(self, request):
        params = request.query_params.get(self.fields_param)
        if params:
            return set(param.strip() for param in params.split(','))

    def filter_queryset(self, request, queryset, view):
        if self.fields_param in request.query_params:
            for field in self.get_fields(request):
                queryset = queryset.filter("exists", field=field)
        return queryset


class MissingFilter(BaseFilterBackend):

    fields_param = getattr(api_settings, 'MISSING_PARAM', 'missing')

    def get_fields(self, request):
        params = request.query_params.get(self.fields_param)
        if params:
            return set(param.strip() for param in params.split(','))

    def filter_queryset(self, request, queryset, view):
        if self.fields_param in request.query_params:
            for field in self.get_fields(request):
                queryset = queryset.filter("missing", field=field)
        return queryset


class FieldsFilter(FilterOptionsMixin, BaseFilterBackend):

    fields_param = getattr(api_settings, 'FIELDS_PARAM', 'fields')

    def get_fields(self, view, request):
        valid = set(self.get_option(view, 'valid', []))
        default = set(self.get_option(view, 'default'))
        include = set(self.get_option(view, 'include', []))
        exclude = set(self.get_option(view, 'exclude', []))
        requested = set()
        params = request.query_params.get(self.fields_param)
        if params:
            requested = set([param.strip() for param in params.split(',')])
        fields = (include | (requested or default) - exclude)
        if valid:
            return fields & valid
        return fields

    def filter_queryset(self, request, queryset, view):
        fields = self.get_fields(view, request)

        if fields:
            return queryset.extra(_source=list(fields))
        return queryset


class TypesFilter(FilterOptionsMixin, BaseFilterBackend):

    fields_param = getattr(api_settings, 'FIELDS_PARAM', 'types')

    def get_types(self, view, request):
        valid = set(self.get_option(view, 'valid', []))
        default = set(self.get_option(view, 'default'))
        include = set(self.get_option(view, 'include', []))
        exclude = set(self.get_option(view, 'exclude', []))
        requested = set()
        params = request.query_params.get(self.fields_param)
        if params:
            requested = set([param.strip() for param in params.split(',')])
        types = (include | (requested or default) - exclude)
        if valid:
            return types & valid
        return types

    def filter_queryset(self, request, queryset, view):
        types = self.get_types(view, request)
        for type in types:
            queryset = queryset.filter("type", value=type)
        return queryset


class MinScoreFilter(BaseFilterBackend):

    min_score_param = getattr(api_settings, 'MIN_SCORE_PARAM', 'min_score')

    def get_min_score(self, request):
        min_score = request.query_params.get(self.min_score_param, None)
        if min_score:
            try:
                return float(min_score)
            except ValueError:
                raise ParseError("Invalid value for '{}'".format(self.min_score_param))

    def filter_queryset(self, request, queryset, view):
        min_score = self.get_min_score(request)
        if min_score:
            queryset = queryset.extra(min_score=min_score)
        return queryset


class OrderingFilter(FilterOptionsMixin, filters.OrderingFilter):
    """
    Same as default OrderingFilter, with identical view properties for ordering param and default ordering.

    Example::

        class YourView(APIView):

            ordering_filter_options = {
                "fields": ["id", "created", "updated", "start", "end", "rank", "duration", "country", "labels"],
                "field_map": {
                    "title": "title.raw"
                },
                "reversed": ["rank"],
                "default": ["-start"]
            }

    """
    special_reversed_fields = ["_score"]
    special_field_map = {"relevance": "_score"}

    def get_valid_fields(self, view):
        """
        Get fields that can be used to sort via the url

        """
        return self.get_option(view, 'fields', []) + self.get_option(view, 'field_map', {}).keys() + self.special_field_map.keys()

    def get_reversed_fields(self, view):
        """
        Get list of fields for which ordering should be reversed (- is ascending instead of descending, e.g. _score)
        """
        return self.get_option(view, 'reversed', []) + self.special_reversed_fields

    def get_field_map(self, view):
        """
        Get url name to storage name mapping

        """
        field_map = self.get_option(view, 'field_map', {})
        field_map.update(self.special_field_map)
        return field_map

    def get_ordering(self, request, queryset, view):
        """
        Prepare ordering directives based on valid fields, field map and reversed fields

        """
        params = request.query_params.get(self.ordering_param)

        if params:
            valid_fields = self.get_valid_fields(view)
            directives = (param.strip() for param in params.split(',') if param.strip().lstrip('-') in valid_fields)
        else:
            directives = self.get_default_ordering(view)

        if not directives:
            return

        field_map = self.get_field_map(view)
        reversed_fields = self.get_reversed_fields(view)
        ordering = []
        for directive in directives:
            name = directive.lstrip('-')
            field = field_map.get(name, name)
            if name in reversed_fields or field in reversed_fields:
                direction = 'asc' if directive.startswith('-') else 'desc'
            else:
                direction = 'desc' if directive.startswith('-') else 'asc'
            ordering.append({six.text_type(field): {six.text_type("order"): six.text_type(direction)}})
        return ordering


    def get_default_ordering(self, view):
        """
        Extract default ordering from ordering_filter_options.default, or use the view's ordering property

        """
        return self.get_option(view, 'default', None) or super(OrderingFilter, self).get_default_ordering(view)

    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)
        if ordering:
            queryset = queryset.sort(*ordering)
        return queryset
