"Core exceptions raised by the package of common-utils."
#! /usr/bin/env python
# coding=UTF-8

class CommonUtilsError(Exception):
    pass

class SystemCommandExecuteError(CommonUtilsError):
    pass

class UnSupportedMethodError(CommonUtilsError):
    pass

class ConnectTimeoutError(CommonUtilsError):
    pass

class TransferFilesError(CommonUtilsError):
    pass