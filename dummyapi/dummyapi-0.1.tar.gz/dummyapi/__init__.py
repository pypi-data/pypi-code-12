#!/usr/bin/env python

"""
  Author:  Yeison Cardona --<yeison.eng@gmail.com>
  Purpose:
  Created: 22/10/15
"""

import requests

########################################################################
class NewAPI:
    """"""
    FORMAT = None

    #----------------------------------------------------------------------
    def __init__(self, token=None):
        """"""

        if token:
            self.headers = {'Authorization': "JWT {}".format(token)}
        else:
            self.headers = {}

        self.__endpoints__ = self.endpoints()

        assert self.__endpoints__, "No endpoinds, API is running?"


    #----------------------------------------------------------------------
    def endpoints(self):
        """"""
        response = requests.get(self.HTTP_SERVICE, headers=self.headers)
        if response.ok:
            return response.json()
        else:
            return None
            # raise Exception(response.reason)


    #----------------------------------------------------------------------
    def options(self, endpoint=""):
        """"""
        response = requests.options(self.HTTP_SERVICE+endpoint, headers=self.headers)
        return response.json()


    #----------------------------------------------------------------------
    def __request__(self, call, mode, files, **kwargs):
        """"""
        kwargs = self.__fix_lists__(kwargs)
        if mode in ['put', 'post']:
            response = getattr(requests, mode)(self.HTTP_SERVICE+call+"/", data=kwargs, files=files, headers=self.headers)
        else:
            response = getattr(requests, mode)(self.HTTP_SERVICE+call+"/", params=kwargs, files=files, headers=self.headers)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            return "Error {}:{}".format(response.status_code, response.reason)


    #----------------------------------------------------------------------
    def __fix_lists__(self, kwargs):
        """"""
        data = {}
        for kw in  kwargs:
            if isinstance(kwargs[kw], (list, dict)):
                # data[kw] = ("[" + "{}," * len(kwargs[kw]) + "]").format(*kwargs[kw])
                data[kw] = str(kwargs[kw])

            # elif isinstance(kwargs[kw], dict):
                # data[kw] = str(kwargs[kw])

            else:
                data[kw] = kwargs[kw]

        return data


    #----------------------------------------------------------------------
    def __getattr__(self, api):
        """"""

        mode = 'get'
        for prefix in ['post', 'put', 'get', 'delete', 'options', 'head']:

            if api.startswith('{}_'.format(prefix)):
                api = api.replace('{}_'.format(prefix), '')
                mode = prefix
                break

        if api in self.__endpoints__.keys():

            def f(**kwargs):

                if "files" in kwargs:
                    files = kwargs.pop("files")
                else:
                    files = {}

                if "endpoint" in kwargs:
                    endpoint = kwargs.pop("endpoint")
                    attr = "{}/{}".format(attr, endpoint)
                else:
                    attr = api

                if self.FORMAT:
                    request = self.__request__(attr, mode, files, **kwargs)
                    if isinstance(request, (str, bytes)):
                        return self.FORMAT(request)
                    else:
                        return request
                else:
                    return self.__request__(attr, mode, files, **kwargs)

            return f


        else:
            raise AttributeError("Endpoint '{}' not found".format(attr))
