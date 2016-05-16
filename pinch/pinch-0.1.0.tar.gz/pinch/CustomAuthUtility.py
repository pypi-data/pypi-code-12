# -*- coding: utf-8 -*-

'''
 PinchLib

 This file was automatically generated for Pinch by APIMATIC v2.0 ( https://apimatic.io ) on 05/13/2016
'''
from Configuration import *

class CustomAuthUtility:

    @staticmethod
    def appendCustomAuthParams(http_request):
        ''' Add custom authentication to the request.

        Args:
            http_request (HttpRequest object): The HttpRequest object with fields you can modify.
        '''

        # TODO: Add your custom authentication here
        # The following properties are available to use
        #     Configuration.x_api_token
        #     Configuration.x_api_email
        # 
        # example: 
        # Add a header through: http_request.headers["key"] = "value"
