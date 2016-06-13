# -*- coding: utf-8 -*-


class ApiError(Exception):
    pass


class UnauthorizedError(ApiError):
    pass
