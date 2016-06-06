# -*- coding: utf-8 -*-
from __future__ import absolute_import

from penapi.pentaho import (
    Pentaho,
    PentahoBasicAuth,
    PentahoCookieAuth,
    PENTAHO_DEFAULT_COOKIE_NAME
)


_pentaho_obj = Pentaho()

users = _pentaho_obj.users
roles = _pentaho_obj.roles


def set_basic_auth_method(username, password):
    _pentaho_obj.set_auth_method(PentahoBasicAuth(username, password))


def set_cookie_auth_method(cookie_value, cookie_name=PENTAHO_DEFAULT_COOKIE_NAME):
    _pentaho_obj.set_auth_method(PentahoCookieAuth(cookie_value, cookie_name))


def renew_cookie_value(cookie_value, cookie_name=PENTAHO_DEFAULT_COOKIE_NAME):
    set_cookie_auth_method(cookie_value, cookie_name)


def set_pentaho_base_url(pentaho_base_url):
    _pentaho_obj.set_pentaho_base_url(pentaho_base_url)


def set_ssl_check(ssl_check):
    _pentaho_obj.set_ssl_check(ssl_check)
