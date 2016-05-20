# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

class AppSensorMeta(object):
    def __init__(self, remote_address, method, location, route_id, session_id=None, user_id=None, transaction_id=None):
        self.remote_address = remote_address
        self.method = method
        self.location = location
        self.route_id = route_id
        self.session_id = session_id
        self.user_id = user_id
        self.transaction_id = transaction_id

        self.get_dict = None
        self.post_dict = None
        self.cookie_dict = None
        self.json_body_str = None
        self.request_content_len = None
        self.response_code = None
        self.do_request = False
        self.do_response = False
        self.user_agent_str = False

    def request_data(
            self,
            request_content_len=None,
            get_dict=None,
            post_dict=None,
            cookie_dict=None,
            json_body_str=None,
            user_agent_str=None):
        self.do_request = True
        self.get_dict = get_dict
        self.post_dict = post_dict
        self.cookie_dict = cookie_dict
        self.json_body_str = json_body_str
        self.request_content_len = request_content_len
        self.user_agent_str = user_agent_str

    def response_data(self, response_content_len=None, response_code=None):
        self.do_response = True
        self.response_content_len = response_content_len
        self.response_code = response_code
