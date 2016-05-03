from swagger.swagger_client.apis.exportresource_api import ExportresourceApi
from swagger.swagger_client.configuration import Configuration
from swagger.swagger_client.rest import ApiException
from urllib3.exceptions import HTTPError

class HttpExecutor:
    def __init__(self):
        self.RETRIES = 3

    # throws HTTPError
    def execute_with_retry(self, request, *arguments, **kw_arguments):
        for i in range(self.RETRIES+1):
            r = request(*arguments, **kw_arguments)
            if r.status != 200:
                if i < self.RETRIES:
                    if r.status not in (500, 504) or r.status not in (400, 403):
                        raise ApiException(http_resp=r)
                else:
                    raise ApiException(http_resp=r)
            else:
                return r