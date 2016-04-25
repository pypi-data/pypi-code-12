# -*- coding: utf-8 -*-
__author__ = 'dzazra'


def load(mode="sign", key_password="", cert_private="", cert_public="", cert_ca="", cert_ca_crl=""):
    """
    :param mode: "sign" or "verify"
    :param key_password: password
    :return:
    """
    # Contact java server
    from py4j.java_gateway import JavaGateway
    from py4j.protocol import register_input_converter
    from py4j.java_gateway import JavaClass
    import time
    import datetime

    class DateConverter(object):
        def can_convert(self, obj):
            return isinstance(obj, datetime.date)

        def convert(self, obj, gateway_client):
            Date = JavaClass("java.sql.Date", gateway_client)
            return Date.valueOf(obj.strftime("%Y-%m-%d"))

    class DatetimeConverter(object):
        def can_convert(self, obj):
            return isinstance(obj, datetime.datetime)

        def convert(self, obj, gateway_client):
            Timestamp = JavaClass("java.sql.Timestamp", gateway_client)
            return Timestamp(int(time.mktime(obj.timetuple())) * 1000 + obj.microsecond // 1000)

    gateway = JavaGateway(auto_convert=True)
    capi = gateway.entry_point

    # datetime is a subclass of date, we should register DatetimeConverter first
    register_input_converter(DatetimeConverter())
    register_input_converter(DateConverter())

    if mode == 'sign':
        # Load pkey and test password
        capi.initSignatureMode(cert_private, key_password, cert_public)
        capi.createSignature
    else:
        capi.initVerificationMode(cert_ca, cert_ca_crl)
        capi.verifySignature

    return capi