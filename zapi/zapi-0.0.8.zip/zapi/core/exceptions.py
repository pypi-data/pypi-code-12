#!/usr/bin/env python
#-*- coding:utf8 -*-
__author__ = 'zhonghong'


import logging

LOG = logging.getLogger(__name__)


class ZapiException(Exception):
    """Base zapi Exception
    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.
    """
    msg_fmt = "An unknown exception occurred."
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.msg_fmt % kwargs

            except Exception:
                # kwargs doesn't match a variable in the message
                # log the issue and the kwargs
                LOG.exception('Exception in string format operation')
                for name, value in kwargs.iteritems():
                    LOG.error("%s: %s" % (name, value))    # noqa

                message = self.msg_fmt

        self.message = message
        super(ZapiException, self).__init__(message)

    def format_message(self):
        # NOTE(mrodden): use the first argument to the python Exception object
        # which should be our full ZapiException message, (see __init__)
        return self.args[0]



class Invalid(ZapiException):
    msg_fmt = "Unacceptable parameters."
    code = 400



class NotFound(ZapiException):
    msg_fmt = "Resource could not be found."
    code = 404


class ModelNotFound(NotFound):
    msg_fmt = "Model %(model)s could not be found."


class ClassNotFound(NotFound):
    msg_fmt = "Class %(class_name)s could not be found: %(exception)s"


