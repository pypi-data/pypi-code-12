# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.django import appsensor_login_failed

import os
from tcell_agent.sensor_events import LoginEvent, HoneytokenSensorEvent
from tcell_agent.instrumentation import handle_exception, safe_wrap_function
from tcell_agent.instrumentation.django.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.django.utils import header_keys_from_django_request

import logging
import tcell_agent.tcell_logger
LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

def _instrument_common_auth():
    pass
    # old_process_authenticate = AuthenticationForm.clean
    # def clean(self):
    #     try:
    #         retval = old_process_authenticate(self)
    #             if (self.user_cache is not None):
    #                 print("User logged in")
    #                 self.
    #     except Exception as e:
    #         raise e
    #     return retval
    # AuthenticationForm.clean = clean

def _userLoggedIn(sender, user, request, **kwargs):
    def _set_login_success():
        #request._tcell_signals['login_success'] = True
        # put appsensor stuff here
        pass
    def _set_loginfraud_success():
        login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
        if login_policy is None or login_policy.login_success_enabled != True:
            return
        request = GlobalRequestMiddleware.get_current_request()
        if request is not None:
            username = None
            try:
                username = user.get_username()
            except:
                pass
            if request:
                try:
                    if request.method == "POST":
                        username = request.POST.get("user", username)
                        username = request.POST.get("email", username)
                        username = request.POST.get("email_address", username)
                        username = request.POST.get("username", username)
                    else:
                        username = request.GET.get("username", username)
                except Exception as e:
                    LOGGER.error("Could not determine username for login success event")
                    LOGGER.debug(e)
            LOGGER.debug("Login success event for {username}".format(username=username))
            event = LoginEvent().success(
                user_id=username, 
                user_agent=request.META.get("HTTP_USER_AGENT", None),
                referrer=request.META.get("HTTP_REFERER", None),
                remote_addr=request._tcell_context.remote_addr,
                header_keys=header_keys_from_django_request(request),
                document_uri=request._tcell_context.fullpath,
                session_id=request._tcell_context.session_id)
            TCellAgent.send(event)
    safe_wrap_function("Setting login success", _set_login_success) 
    safe_wrap_function("LoginFraud login success", _set_loginfraud_success) 

def _userLoginFailed(sender, credentials, **kwargs):
    def _set_loginfraud_failure():
        login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
        if login_policy is None or login_policy.login_failed_enabled != True:
            return
        request = GlobalRequestMiddleware.get_current_request()
        if request is not None:
            username = None
            if credentials:
                username = credentials.get("username")
            LOGGER.debug("Login failed event for {username}".format(username=username))
            event = LoginEvent().failure(
                user_id=username, 
                user_agent=request.META.get("HTTP_USER_AGENT", None),
                referrer=request.META.get("HTTP_REFERER", None),
                remote_addr=request._tcell_context.remote_addr,
                header_keys=header_keys_from_django_request(request),
                document_uri=request._tcell_context.fullpath,
                session_id=request._tcell_context.session_id)
            TCellAgent.send(event)
    safe_wrap_function("LoginFraud login failure", _set_loginfraud_failure) 

def _addUserLoginSignals():
    user_logged_in.connect(_userLoggedIn)
    user_login_failed.connect(_userLoginFailed)

def _addAuthIntercept():
    original_auth = ModelBackend.authenticate
    def authenticate(self, username=None, password=None, **kwargs):
        def _check_honeytoken_creds():
            request = GlobalRequestMiddleware.get_current_request()
            if request:
                honeytoken_policy = TCellAgent.get_policy(PolicyTypes.HONEYTOKEN)
                if honeytoken_policy:
                    token_id = honeytoken_policy.get_id_for_credential(username, password)
                    if token_id:
                        event = HoneytokenSensorEvent(
                            token_id=token_id,
                            remote_addr=request._tcell_context.remote_addr
                        )
                        TCellAgent.send(event)
        safe_wrap_function("Honeytokens check", _check_honeytoken_creds) 
        return original_auth(self, username, password, **kwargs)
    ModelBackend.authenticate = authenticate

try:
    import django
    from django.contrib.auth.forms import AuthenticationForm
    if TCellAgent.tCell_agent:
        _instrument_common_auth()
        from django.contrib.auth.signals import user_logged_in, user_login_failed
        from django.db.backends.signals import connection_created
        safe_wrap_function("Adding user login signals", _addUserLoginSignals)
        from django.contrib.auth.backends import ModelBackend
        safe_wrap_function("Adding user honeytoken code", _addAuthIntercept)
except Exception as e:
    LOGGER.debug("Could not instrument django common-auth")
    LOGGER.debug(e)

