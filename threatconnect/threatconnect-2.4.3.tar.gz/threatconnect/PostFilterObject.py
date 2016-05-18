""" custom """
import SharedMethods
from Config.FilterOperator import FilterOperator
from ErrorCodes import ErrorCodes


class PostFilterObject(object):
    """ object to store post filter values for processing after api request """
    def __init__(self):
        """ """
        self._description = None
        self._filter = None
        self._method = None
        self._operator = None

    def set_description(self, data):
        """ set post filter description """
        self._description = SharedMethods.uni(data)

    def set_filter(self, data):
        """ set post filter data to filter on """
        self._filter = SharedMethods.uni(data)

    def set_method(self, data):
        """ set post filter method name for getattr """
        self._method = SharedMethods.uni(data)

    def set_operator(self, data_enum):
        """ set post filter operator for comparison """
        if isinstance(data_enum, FilterOperator):
            self._operator = data_enum
        else:
            raise AttributeError(ErrorCodes.e1010.value.format(data_enum))

    @property
    def description(self):
        """ post filter description """
        return self._description

    @property
    def filter(self):
        """ post filter data to filter on """
        return self._filter

    @property
    def method(self):
        """ post filter method name for getattr """
        return self._method

    @property
    def operator(self):
        """ post filter operator for comparison """
        return self._operator

    def __str__(self):
        """ allow object to be displayed with print """

        printable_string = '\n{0!s:_^80}\n'.format('Post Filter Object')

        #
        # filter properties
        #
        printable_string += '{0!s:40}\n'.format('Filter Properties')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('description', self.description))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('filter', self.filter))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('method', self.method))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('operator', self.operator))

        return printable_string
