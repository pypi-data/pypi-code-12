#!/usr/bin/env python
#  -*- coding: utf-8 -*-

class DockerflyException(Exception):

    def __init__(self, message, errno):
        super(DockerflyException, self).__init__(message)
        self._message =  message
        self._errno = errno

    def __str__(self):
        return repr('"errno":{}, "errMsg":{}'.format(self._errno, self._message))

    @property
    def message(self):
        return self._message

    @property
    def errno(self):
        return self._errno

class VEthCreateException(DockerflyException):

    def __init__(self, message, errno=100):
        super(VEthCreateException, self).__init__(message, errno)

class VEthUpException(DockerflyException):

    def __init__(self, message, errno=101):
        super(VEthUpException, self).__init__(message, errno)

class VEthDownException(DockerflyException):

    def __init__(self, message, errno=102):
        super(VEthDownException, self).__init__(message, errno)

class VEthDeleteException(DockerflyException):

    def __init__(self, message, errno=103):
        super(VEthDeleteException, self).__init__(message, errno)

class VEthAttachException(DockerflyException):

    def __init__(self, message, errno=104):
        super(VEthAttachException, self).__init__(message, errno)

class VEthStatusException(DockerflyException):

    def __init__(self, message, errno=105):
        super(VEthStatusException, self).__init__(message, errno)

class ContainerActionError(DockerflyException):
    def __init__(self, message, errno=201):
        super(ContainerActionError, self).__init__(message, errno)
