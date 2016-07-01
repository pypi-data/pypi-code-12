import urllib2
import urllib
import json


class QuayError(Exception):
    def __init__(self, code, message, response, http_error):
        super(QuayError, self).__init__(message)
        self.cause = http_error
        self.code = code
        self.response = response


class Client():
    def __init__(self,
                 token=None):
        self.token = token
        self.base_url = 'https://quay.io/api/v1'

    def __perform_request__(self, request, verbose={}):
        if self.token:
            request.add_header('Authorization', 'Bearer %s' % self.token)
        try:
            stream = urllib2.urlopen(request)
            response = stream.read()
            verbose['info'] = stream.info().dict
            stream.close()
            return response
        except urllib2.HTTPError as e:
            response = e.read()
            error = QuayError(
                code=e.code,
                message=response,
                response=response,
                http_error=e)

            raise error

    def __clean_data__(self, data):
        return {k: v for k, v in data.items() if v is not None and v != ''}

    def __get__(self, base_url, uri, data={}, verbose={}):
        endpoint = "%s/%s" % (base_url, uri)
        request = urllib2.Request(endpoint)
        request.get_method = lambda: 'GET'
        return self.__perform_request__(request, verbose)

    def security(self, repository, imageid):
        uri = 'repository/%s/image/%s/security' % (repository, imageid)
        response = self.__get__(self.base_url, uri)

        return json.loads(response)
