# -*- coding: utf-8 -*-


class JsonError(Exception):
    """
    Base error raised in this package.
    """

    pass


class JsonValidationError(JsonError):
    """
    Validation error.
    """

    pass


class JsonTransformationError(JsonError):
    """
    Transformation error.
    """

    pass
