from werkzeug.exceptions import *
from flask_restful import HTTPException
from collections import OrderedDict


class ZeusHTTPException(HTTPException):
    """
    code http状态码
    description 错误描述
    """

    def __init__(self, description=None, response=None, error_code=0, details=None):
        """
        :param description: 自定义错误描述
        :param response: 自定义响应数据
        :param error_code: 自定义错误代码
        :param details: 自定义错误详情
        :return:
        """
        self.status_code = self.code
        self.message = description or self.description
        self.error_code = error_code
        self.details = details or {}
        super(ZeusHTTPException, self).__init__(description, response)

    def as_dict(self):
        """
        :return: {
            'status_code': ...,
            'error_code': ...,
            'message': ...,
            'details': ...
        }
        """
        data = OrderedDict()
        for k in ['status_code', 'error_code', 'message', 'details']:
            data[k] = getattr(self, k)
        return data

    @property
    def data(self):
        return self.as_dict()


class ZeusBadRequest(BadRequest, ZeusHTTPException):
    """ 400
    """
    pass


class ZeusUnauthorized(Unauthorized, ZeusHTTPException):
    """ 401
    """
    pass


class ZeusNotFound(NotFound, ZeusHTTPException):
    """ 404
    """
    pass


class ZeusMethodNotAllowed(MethodNotAllowed, ZeusHTTPException):
    """ 405
    """
    pass