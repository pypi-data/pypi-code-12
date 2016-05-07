import urllib

try:
    import simplejson as json
except :
    import json


from httplib2 import http


__all__ = [
    'DFAASApiClient'
]

################################################################################

class HttpException(Exception):
    def __init__(self, code, reason, error='Unknown Error'):
        self.code = code
        self.reason = reason
        self.error_message = error
        super(HttpException, self).__init__()

    def __str__(self):        
        return '\n Status: %s \n Reason: %s \n Error Message: %s\n' % (self.code, self.reason, self.error_message)

################################################################################


class HttpApiClient(object):
    """
    Base implementation for an HTTP
    API Client. Used by the different
    API implementation objects to manage
    Http connection.
    """

    def __init__(self, api_key, base_url):
        """Initialize base http client."""
        self.conn = http()
        # DFAAS API key
        self.api_key = api_key
        #base url 
        self.base_url = base_url
        
    def _http_request(self, service_type, **kwargs):
        """
        Perform an HTTP Request using base_url and parameters
        given by kwargs.
        Results are expected to be given in JSON format
        and are parsed to python data structures.
        """
        request_params = urllib.urlencode(kwargs)
        request_params = request_params.replace('%28', '').replace('%29', '')

        uri = '%s%s?api_key=%s&%s' % \
            (self.base_url, service_type, self.api_key, request_params)
        header, response = self.conn.request(uri, method='GET')
        return header, response

    def _http_uri_request(self, uri):
        header, response = self.conn.request(uri, method='GET')
        return header, response

    def _is_http_response_ok(self, response):
        return response['status'] == '200' or response['status'] == 200

    def _get_params(self, regions = None, subpops = None, format = None, type = None,tracking = None):


        params = {}

        if regions:
            params['regions'] = regions
        if subpops:
            params['subpops'] = subpops
        if format:
            params['format'] = format
        if tracking:
            params['tracking'] = tracking
        if type:
            params['type'] = type


        return params


    def _create_query(self, category_type, params):
        header, content = self._http_request(category_type + '/', **params)
        resp = json.loads(content)
        if not self._is_http_response_ok(header):
            error = resp.get('error_message', 'Unknown Error')
            raise HttpException(header.status, header.reason, error) 
        return resp


################################################################################

class DFAASApiClient(HttpApiClient):

    def __init__(self, api_key,ip):
        self.ip = ip
        self.api_url  = 'http://' + ip
        base_url = self.api_url
        super(DFAASApiClient, self).__init__(api_key, base_url)


    def spawn(self, regions = None, subpops = None, format = None, type = None):
        """
        Spawns/Starts a filtering job in DFAAS
        # For eg regions=1:900-1000&&subpops=CHB&format=reformat&nfs=yes
        
        Args: 
        *Note that none of the arguments are required
          regions         : Filter criteria
            type : [string]
          subpops          : Sub population code (if need to be narrowed)
            type : [string]
          format          : Whether to reformat
            type : [string]
          nfs            : Use NFS or S3
            type : [string]

        Returns:
          Tracking Id in a string form

        Raises:
          HttpException with the error message from the server
        """

        params = self._get_params(regions = regions, subpops = subpops, format = format, type = type)

        return self._create_query('spawn', params)

    def status(self, tracking=None):
        """
        Takes the tracking id and gives the status

        Args: 
          tracking id: Identifier of the filtering job - Fetched from spawn

        Returns:
          Job id with status

        Raises:
          HttpException with the error message from the server
        """
        params = self._get_params(tracking = tracking)

        return self._create_query('status', params)

    def insight(self, tracking=None, type=None):
        """
        Stats of the Job

        
        Args: 
            tracking          : Trackig Id
              type : [string]
            type          : Type of metric
              type : [string]

        Returns:
          Basic status of the filtering job

        Raises:
          HttpException with the error message from the server
        """

        params =  self._get_params(tracking = tracking, type = type)

        return self._create_query('insight', params)


################################################################################    
