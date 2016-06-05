from django.conf import settings


class TxtLocalAPI(object):
    API_VERSION = "2.0"
    API_HOST = "api.txtlocal.com"
    API_PORT = 443
    API_HTTPS = True
    API_PROXY = None
    API_PROXY_PORT = None

    API_SEND_URL = "/send"

    USERNAME_PARAM_NAME = "username"
    HASH_PARAM_NAME = "hash"
    API_KEY_PARAM_NAME = "apiKey"
    FORMAT_PARAM_NAME = "format"


    @staticmethod
    def set_proxy(proxy, port):
        '''
        Enable using a Proxy to connect through
        @param $proxy The proxy server
        @param $port The proxy port number
        '''
        TxtLocalAPI.API_PROXY = proxy
        TxtLocalAPI.API_PROXY_PORT = port


    def __init__(self, username=None, hash=None, apiKey=None):
        '''
        Create an instance of the class with the username and key obtained from txtlocal.
        @param $username
        @param $apiKey
        '''
        self.username = username or settings.API_SMS_USERNAME if hasattr(settings, 'API_SMS_USERNAME') else None
        self.hash = hash or settings.API_SMS_HASH if hasattr(settings, 'API_SMS_HASH') else None
        self.apiKey = apiKey or settings.API_SMS_KEY if hasattr(settings, 'API_SMS_KEY') else None
        if not self.hash and not self.apiKey:
            raise ValueError(
                "At least one of API_SMS_HASH/API_SMS_KEY is required."
            )
        self.sender = settings.DEFAULT_SMS_SENDER if hasattr(settings, 'DEFAULT_SMS_SENDER') else None

    def _http(self, method, url, x_headers=None, params=None):
        '''
        HTTP Request to the specified API endpoint
        @param $string $url
        @param $string $x_headers
        @return LatchResponse
        '''
        try:
            # Try to use the new Python3 HTTP library if available
            import http.client as http
            import urllib.parse as urllib
        except:
            # Must be using Python2 so use the appropriate library
            import httplib as http
            import urllib

        if x_headers is not None:
            all_headers = x_headers
        else:
            all_headers = dict()

        if TxtLocalAPI.API_PROXY != None:
            if TxtLocalAPI.API_HTTPS:
                conn = http.HTTPSConnection(TxtLocalAPI.API_PROXY, TxtLocalAPI.API_PROXY_PORT)
                conn.set_tunnel(TxtLocalAPI.API_HOST, TxtLocalAPI.API_PORT)
            else:
                conn = http.HTTPConnection(TxtLocalAPI.API_PROXY, TxtLocalAPI.API_PROXY_PORT)
                url = "http://" + TxtLocalAPI.API_HOST + url
        else:
            if TxtLocalAPI.API_HTTPS:
                conn = http.HTTPSConnection(TxtLocalAPI.API_HOST, TxtLocalAPI.API_PORT)
            else:
                conn = http.HTTPConnection(TxtLocalAPI.API_HOST, TxtLocalAPI.API_PORT)

        try:
            if method == "POST" or method == "PUT":
                all_headers["Content-type"] = "application/x-www-form-urlencoded"

            if params is not None:
                x_params = self.add_auth_params(params)
                parameters = urllib.urlencode(x_params)

                conn.request(method, url, parameters, headers=all_headers)
            else:
                conn.request(method, url, headers=all_headers)

            response = conn.getresponse()

            response_data = response.read().decode('utf8')
            conn.close()
            ret = response_data

        except:
            ret = None

        return ret

    def add_auth_params(self, params):
        all_params = params
        if self.apiKey:
            all_params['apiKey'] = self.apiKey
        else:
            all_params['hash'] = self.hash
        all_params['username'] = self.username

        return all_params


    def sendSms(self, number, message, sender=None, sched=None, test=False, receiptURL=None, custom=None,
                optouts=False, simpleReplyService=False):

        if not sender:
            sender = self.sender

        params = {
            'message': message,
            'numbers': number,
            'sender': sender
        }
        return self._http('POST', self.API_SEND_URL + "/", params=params)