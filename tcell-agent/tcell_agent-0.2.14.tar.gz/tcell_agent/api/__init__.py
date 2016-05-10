# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

""" API Module handles all calls to/from the tCell service. Errors are
handled gracefully since it's generally running silently and should
fail open.
"""

from __future__ import unicode_literals
from __future__ import print_function

import threading
import requests
import json
import logging
from tcell_agent.config import CONFIGURATION
from tcell_agent.version import VERSION
import sys

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

class SetEncoder(json.JSONEncoder):    
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

    def encode(self, obj):
        def traverse(obj):
            if isinstance(obj, dict):
                return {k: traverse(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [traverse(elem) for elem in obj]
            elif (isinstance(obj, str) or isinstance(obj, bytes) or (sys.version_info < (3, 0) and isinstance(obj, unicode))) and len(obj) > 256:
                return obj[:256]
            else:
                return obj  # no container, just values (str, int, float)
        return super(SetEncoder, self).encode(traverse(obj))


class TCellAPIException(Exception):
    """Special API Exception"""
    pass

class TCellAPI(object):
    """API Class handling comms"""

    def v1update(self, last_timestamp=None):
        """v1 is the new rest API endpoint"""
        url = '{url}/app/{appname}/update'.format(
            url=CONFIGURATION.tcell_api_url,
            appname=CONFIGURATION.app_id)
        LOGGER.debug("calling api: " + url)
        params = {}
        if last_timestamp:
            params["last_timestamp"] = last_timestamp
        headers = {"Authorization":"Bearer " + CONFIGURATION.api_key,
                   "TCellAgent":"Python " + VERSION}
        try:
            response = requests.get(url, params=params, headers=headers, allow_redirects=False)
        except Exception as general_exception:
            LOGGER.debug(general_exception)
            raise TCellAPIException("could not connect to server")
        LOGGER.debug("response: " + str(response))
        if response.ok:
            try:
                response_json = response.json()
                if response_json.get("result") is not None:
                    result = response_json.get("result")
                    return result
                else:
                    return None
            except Exception as general_exception:
                LOGGER.debug(general_exception)
                raise TCellAPIException("Result field not found")
        LOGGER.debug(response)
        raise TCellAPIException("Response was not 'ok'")

    def v1send_events(self, events, event_wrap_name=None, event_endpoint=None):
        """
        Sends events to tCell via the API
        v1 is the new rest API
        """
        if event_wrap_name is None:
            event_wrap_name = "events"
        if event_endpoint is None:
            event_endpoint = "server_agent"
        url = '{url}/app/{appname}/{endpoint}'.format(
            url=CONFIGURATION.tcell_input_url,
            appname=CONFIGURATION.app_id,
            endpoint=event_endpoint)
        payload = {"hostname": CONFIGURATION.host_identifier,
                   "uuid": CONFIGURATION.uuid
                  }
        payload[event_wrap_name] = events
        LOGGER.debug("sending events to " + url)
        LOGGER.debug(json.dumps(payload, cls=SetEncoder))
        headers = {"Authorization":"Bearer " + CONFIGURATION.api_key,
                   "Content-type":"application/json",
                   "TCellAgent":"Python " + VERSION}
        response = requests.post(url, data=json.dumps(payload, cls=SetEncoder), headers=headers, allow_redirects=False)
        LOGGER.debug("send_events response: " + str(response))
        # who cares if it succeeded?
        return response

    def v0api(self, api_call, last_timestamp=None):
        """Some legacy support for old configs, don't use this"""
        url = '{url}/api/{appname}{api_call}/{secret}'.format(
            url=CONFIGURATION.tcell_api_url,
            appname=CONFIGURATION.app_id,
            secret=CONFIGURATION.api_key,
            api_call=api_call)
        params = {}
        if last_timestamp:
            params["last_timestamp"] = last_timestamp
        LOGGER.debug("calling OLD api: " + url)
        response = requests.get(url, params=params)
        LOGGER.debug("old API response: " + str(response))
        if response.ok:
            try:
                response_json = response.json()
                if response_json.get("result") is not None:
                    result = response_json.get("result")
                    return result
                else:
                    return None
            except Exception as general_exception:
                LOGGER.exception(general_exception)
                raise TCellAPIException("Result field not found")
        raise TCellAPIException("Response Failed")

    @classmethod
    def send_events(cls, events, event_wrap_name=None, event_endpoint=None):
        """Want to manually send events? This is your method!"""
        try:
            cls.static_api
        except AttributeError:
            cls.static_api = cls()
        try:
            return cls.static_api.v1send_events(
                events,
                event_wrap_name=event_wrap_name,
                event_endpoint=event_endpoint)
        except Exception as sending_exception:
            LOGGER.error("Exception while sending TCell event.")
            LOGGER.exception(sending_exception)
