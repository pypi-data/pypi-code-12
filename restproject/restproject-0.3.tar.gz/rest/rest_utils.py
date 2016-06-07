import requests
import json

from utils.mode_utils import mode

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class rest_utils(mode):
    
    def __init__(self,
                 mgmt_ip,
                 username,
                 password):
        self.mgmt_ip = mgmt_ip
        self.username = username
        self.password = password
        self.auth_cookies = None

    def _request(self,
                 method,
                 url,
                 payload = None,
                 auth = False):
        
        log.info("_request method called with method as {0}, url as {1} and \
                        payload as {2}".format(method, url, payload)) 

        ret_val, status_code = None, None
        try:
            res = requests.request(method, url, cookies = self.auth_cookies, data = payload)
            log.info("result is {0}".format(res.status_code))
            log.info("ret_val is {0}".format(res.content))
            if res:
                ret_val = json.loads(res.content.decode('utf-8'))
                status_code = res.status_code
                log.info(" ret_sc is {0}".format(ret_val))
                if auth is True:
                    self.auth_cookies = res.cookies
        except requests.exceptions.ConnectionError as err:
            log.error('Connection failed: {0}'.format(err.message))
            return None
        except requests.exceptions.HTTPError as err:
            log.error('HTTP error: {0}'.format(err.message))
            return None
        return ret_val, status_code

    def rest_authenticate(self):
        # Method for authenticating with the device and setting the cookies
        log.info("Authenticating with DUT")
        url = "http://{0}/api/aaaLogin.json".format(self.mgmt_ip)
        log.info("URL for rest_authenticate is {0}".format(url))
        payload = '{"aaaUser" : { "attributes" : {"name" : "%s", "pwd" : "%s"}}}' % (self.username, self.password)
        content, status_code = self._request("POST", url, payload, True)
        


    def get(self,
            uri):

        self.rest_authenticate()
        log.info("URL for this Rest Get is {0}".format(uri))
        content, status_code = self._request("GET", uri)
       
        log.info("response: {0}, content: {1}".format(status_code, content)) 
        return status_code, content 


    def post(self,
             uri,
             payload):

        self.rest_authenticate()
        log.info("URL for rest_post is {0}".format(uri))
        content, status_code = self._request("POST", uri, payload)

        log.info("response: {0}, content: {1}".format(status_code, content)) 
        return status_code, content

    def delete(self,
               uri):
        
        self.rest_authenticate()
        log.info("URL for rest_delete is {0}".format(uri))
        content, status_code = self._request("DELETE", uri)

        log.info("response: {0}, content: {1}".format(status_code, content))
