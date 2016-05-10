# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.manager import app_sensor_manager
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation import safe_wrap_function

def django_meta(request):
  meta = AppSensorMeta(
      request._tcell_context.remote_addr ,
      request.META.get("REQUEST_METHOD"),
      request.build_absolute_uri(),
      request._tcell_context.route_id,
      session_id=request._tcell_context.session_id,
      user_id=request._tcell_context.user_id
  )
  return meta

def appsensor_login_failed(request, username):
    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appsensor_policy is None:
        return
    meta = django_meta(request)
    appsensor_policy.check_login_failure(meta, username)

def django_request_appsensor(request):
    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appsensor_policy is None:
        return
    meta = django_meta(request)
    request_len = None
    try:
      request_len = int(request.META.get("CONTENT_LENGTH",0))
    except:
      pass
    request_json_body = None
    try:
      if (request.META.get("CONTENT_TYPE") == "application/json" and request_len < 2000000 and len(request.body) < 2000000):
        request_json_body = request.body
    except Exception as e:
      pass
    meta.request_data(request_len, request.GET, request.POST, request.COOKIES, request_json_body,  request.META.get("HTTP_USER_AGENT"))
    app_sensor_manager.send_appsensor_data(meta)

def django_response_appsensor(django_response, request, response):
    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appsensor_policy is None:
        return
    meta = django_meta(request)
    try:
        if isinstance(response, django_response):
          response_content_len = len(response.content)
    except:
        pass
    response_code = response.status_code
    meta.response_data(response_content_len, response_code)
    app_sensor_manager.send_appsensor_data(meta)
