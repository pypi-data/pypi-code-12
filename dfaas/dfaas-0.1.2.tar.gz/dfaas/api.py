import urllib

try:
    import simplejson as json
except :
    import json


import requests

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
        #self.conn = http()
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

        #uri = '%s%s?%s' % (self.base_url, service_type, self._get_params(**kwargs))
        uri = '%s%s?api_key=%s' % \
            (self.base_url, service_type, self.api_key)
        response = requests.get(uri, params=kwargs)
        return response.headers, response


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
        header, response = self._http_request(category_type , **params)
        resp =  response.text
        if not (response.status_code == requests.codes.ok):
            raise response.raise_for_status()
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

    def jobs(self, tracking=None):
        """
        Returns the details of all the jobs.

        Args:
          (Optional) Tracking Id

        Returns:
          All the jobs

        Raises:
          HttpException with the error message from the server
        """
        params = self._get_params(tracking = tracking)

        return self._create_query('jobs', params)

    def insight(self, tracking=None, type=None):
        """
        Stats of the Job

        
        Args: 
            tracking          : Tracking Id
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
if __name__ == '__main__':
    print("Please enter DFAAS api key with IP(With Port)")
    KEY = 'test'
    IP='localhost:8008/'
    dfaas_client = DFAASApiClient(KEY,IP)
    job_status = dfaas_client.status(tracking = '3e1613c0-21e2-4c1a-ad9c-45fb9370c1a5')
    print("Job Status is " + job_status )
    #With Tracking
    #jobs = dfaas_client.jobs(tracking = '3e1613c0-21e2-4c1a-ad9c-45fb9370c1a5')

    #Without Tracking
    jobs = dfaas_client.jobs()

    print("Jobs " + jobs )
