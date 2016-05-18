""" standard """
import re

""" custom """
from Config.FilterOperator import FilterSetOperator
from ErrorCodes import ErrorCodes


class FilterObject(object):
    """ """
    def __init__(self, tc_obj):
        """ """
        self.tc = tc_obj
        self.tcl = self.tc.tcl  # threatconnect logger

        self._api_filter_names = []
        self._error = False
        self._errors = []
        self._filter_operator = FilterSetOperator.AND
        self._owners = []
        self._post_filter_names = []
        self._post_filters = []
        self._resource_properties = None
        self._resource_type = None
        # self._request_object = None
        self._request_objects = []

    def _add_request_objects(self, data_obj):
        """ add filter object """
        self._request_objects.append(data_obj)

    def add_owner(self, data):
        """ add global owner value for this filter object """
        if isinstance(data, list):
            self._owners.extend(data)
        else:
            self._owners.append(data)

    def add_api_filter_name(self, data):
        """ add api filter names """
        self._api_filter_names.append(data)

    def add_filter_operator(self, data_enum):
        """ add filter operator for set operation """
        if not isinstance(data_enum, FilterSetOperator):
            raise AttributeError(ErrorCodes.e1000.value.format(data_enum))
        else:
            self._filter_operator = data_enum

    def add_post_filter(self, data_obj):
        """ add post filter name """
        self._post_filters.append(data_obj)

    def add_post_filter_names(self, data):
        """ add post filter name """
        self._post_filter_names.append(data)

    @property
    def operator(self):
        """ """
        return self._filter_operator

    @property
    def post_filters(self):
        """ """
        for obj in self._post_filters:
            yield obj

    @property
    def post_filters_len(self):
        """ """
        return len(self._post_filters)

    @property
    def api_filter_names(self):
        """ """
        return sorted(self._api_filter_names)

    @property
    def filters(self):
        """ """
        filters = []
        for resultFilter in sorted(self._api_filter_names):
            if re.findall('^add_', resultFilter):
                filters.append(resultFilter)
        for resultFilter in sorted(self._post_filter_names):
            if re.findall('^add_', resultFilter):
                filters.append(resultFilter)
        return filters

    @property
    def owners(self):
        """ """
        return self._owners

    @property
    def post_filter_names(self):
        """ """
        return sorted(self._post_filter_names)

    # @property
    # def request_object(self):
    #     """ """
    #     return self._request_object

    @property
    def resource_type(self):
        """ """
        return self._resource_type

    def __iter__(self):
        """ """
        for obj in self._request_objects:
            yield obj

    def __len__(self):
        """ """
        return len(self._request_objects)

    def __str__(self):
        """ """
        printable_string = '\n{0:_^80}\n'.format('Filter Object')
        printable_string += '{0:40}\n'.format('Filter Properties')
        printable_string += '  {0:<29}{1:<50}\n'.format('Operator', self.operator)
        printable_string += '  {0:<29}{1:<50}\n'.format('Request Objects', len(self._request_objects))

        if len(self._owners) > 0:
            printable_string += '\n{0:40}\n'.format('Owners')
            for item in self._owners:
                printable_string += '  {0:<29}{1:<50}\n'.format('Owner', item)

        if len(self._request_objects) > 0:
            printable_string += '\n{0:40}\n'.format('Filters')
            for item in self._request_objects:
                printable_string += '  {0:<29}{1:<50}\n'.format('Filter', item.description)

        if len(self._api_filter_names) > 0:
            printable_string += '\n{0:40}\n'.format('API Filters')
            for item in self._api_filter_names:
                printable_string += '  {0:<29}{1:<50}\n'.format('Filter', item)

        if len(self._post_filter_names) > 0:
            printable_string += '\n{0:40}\n'.format('Post Filters')
            for item in self._post_filter_names:
                printable_string += '  {0:<29}{1:<50}\n'.format('Filter', item)

        return printable_string
