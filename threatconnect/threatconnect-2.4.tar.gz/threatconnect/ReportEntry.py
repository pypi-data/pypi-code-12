""" custom """
import SharedMethods


class ReportEntry(object):
    """ """
    __slots__ = (
        '_body',  # request object
        '_content_type',  # request object
        '_data',
        '_description',  # post filter/request object
        '_failure_msg',  # api response
        '_filter',  # post filter object
        '_http_method',  # request object
        '_method',  # post filter object
        '_operator',  # post filter object
        '_payload',  # request object
        '_request_uri',  # request object
        '_request_url',  # api response
        '_resource_type',  # request object
        '_status_code',  # api response
        '_track',  # flag for tracking filters
        '_type')  # ro or pfo

    def __init__(self):
        """ """
        self._body = None
        self._content_type = None
        self._description = None
        self._failure_msg = None
        self._filter = None
        self._http_method = None
        self._method = None
        self._operator = None
        self._payload = None
        self._request_uri = None
        self._request_url = None
        self._resource_type = None
        self._status_code = None
        self._track = False
        self._type = None

    def add_request_object(self, data_obj):
        """ add request object as a report entry """
        self._body = data_obj.body
        self._content_type = data_obj.content_type
        self._description = data_obj.description
        self._http_method = data_obj.http_method
        self._payload = str(data_obj.payload)
        self._request_uri = data_obj.request_uri
        self._resource_type = data_obj.resource_type
        self._track = data_obj.track
        self._type = 'ro'

    def add_post_filter_object(self, data_obj):
        """ add post filter object as a report entry """
        self._description = data_obj.description
        self._filter = data_obj.filter
        self._method = data_obj.method
        self._operator = data_obj.operator
        self._type = 'pfo'

    def set_request_url(self, data):
        """ """
        self._request_url = SharedMethods.uni(data)

    def set_failure_msg(self, data):
        """ """
        self._failure_msg = SharedMethods.uni(data)

    def set_status_code(self, data_int):
        """ """
        self._status_code = SharedMethods.uni(data_int)

    @property
    def body(self):
        """ """
        return self._body

    @property
    def content_type(self):
        """ """
        return self._content_type

    @property
    def description(self):
        """ """
        return self._description

    @property
    def failure_msg(self):
        """ """
        return self._failure_msg

    @property
    def filter(self):
        """ """
        return self._filter

    @property
    def http_method(self):
        """ """
        return self._http_method

    @property
    def method(self):
        """ """
        return self._method

    @property
    def operator(self):
        """ """
        return self._operator

    @property
    def payload(self):
        """ """
        return self._payload

    @property
    def request_uri(self):
        """ """
        return self._request_uri

    @property
    def request_url(self):
        """ """
        return self._request_url

    @property
    def resource_type(self):
        """ """
        return self._resource_type

    @property
    def status_code(self):
        """ """
        return self._status_code

    @property
    def track(self):
        """ """
        return self._track

    @property
    def type(self):
        """ """
        return self._type

    def __str__(self):
        """ add print method to object """

        printable_string = '\n{0!s:_^80}\n'.format('Report Entry')

        #
        # status
        #
        printable_string += '\n{0!s:40}\n'.format('Properties')
        printable_string += ('{0!s:<30}: {1!s:<50}\n'.format('Status Code', self.status_code))
        if self.failure_msg is not None:
            printable_string += ('{0!s:<30}: {1!s:<50}\n'.format('Fail Msg', self.failure_msg))
        printable_string += ('{0!s:<30}: {1!s:<50}\n'.format('Description', self.description))
        printable_string += ('{0!s:<30}: {1!s:<50}\n'.format('Resource Type', self.resource_type))

        #
        # http settings
        #
        printable_string += '\n{0!s:40}\n'.format('HTTP Settings')
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('HTTP Method', self.http_method)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Request URI', self.request_uri)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Request URL', self.request_url)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Content Type', self.content_type)
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Body', self.body)

        #
        # payload
        #
        printable_string += '\n{0!s:40}\n'.format('Payload')
        printable_string += '  {0!s:<29}{1!s:<50}\n'.format('Payload', self.payload)

        return printable_string
