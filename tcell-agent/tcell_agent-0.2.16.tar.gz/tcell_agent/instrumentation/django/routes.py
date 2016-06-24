# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from django.conf import settings

from tcell_agent.agent import TCellAgent
from tcell_agent.sensor_events import AppRouteSensorEvent

import logging
import tcell_agent.tcell_logger
import threading
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

ROUTE_TABLE = {}

def get_route_table():
    return ROUTE_TABLE

def calculate_route_id(uri):
    return str(hash(uri))

def make_route_table(send_events=True):
    def show_urls(urllist, prefix=""):
        for entry in urllist:
            try:
                pattern = entry.regex.pattern
                if pattern is None:
                    continue
                if pattern.startswith("^"):
                    pattern = pattern[1:]
                if pattern.endswith("$"):
                    pattern = pattern[:-1]
                if entry.__class__.__name__ == 'RegexURLPattern':
                    if entry.callback:
                        route_url = prefix + pattern
                        route_target = "unknown"
                        try:
                            if hasattr(entry.callback, 'func_name'):
                                route_target = entry.callback.__module__ + "." + entry.callback.func_name
                            else:
                                route_target = entry.callback.__module__ + "." + entry.callback.__name__
                        except Exception as target_exception:
                            LOGGER.debug("Exception creating target {e}".format(e=target_exception))
                        route_id = calculate_route_id(route_url)
                        ROUTE_TABLE[entry.callback] = {"pattern":route_url,
                                                       "target":route_target,
                                                       "route_id":route_id}
                if hasattr(entry, 'url_patterns'):
                    show_urls(entry.url_patterns, prefix + pattern)
            except Exception as add_route_exception:
                LOGGER.error("Exception parsing route {e}".format(e=add_route_exception))

    def send_route_table():
        try:
            for route_key in ROUTE_TABLE:
                route = ROUTE_TABLE[route_key]
                TCellAgent.discover_route(route.get("pattern"), 
                                          "*",
                                          route.get("target"),
                                          route.get("route_id")
                )
        except Exception as e:
            LOGGER.error("Exception sending route table {e}".format(e=e))

    try:
        root_urlconf = __import__(settings.ROOT_URLCONF)        # access the root urls.py file
        show_urls(root_urlconf.urls.urlpatterns)
        send_route_table_thread = threading.Thread(target=send_route_table, args=())
        send_route_table_thread.daemon = True # Daemonize thread
        send_route_table_thread.start() 
    except Exception as e:
        LOGGER.error("Exception making the route table {e}".format(e=e))
    return get_route_table