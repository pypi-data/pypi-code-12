from api_star.request import RequestMixin
from flask import Request


class APIRequest(RequestMixin, Request):
    pass
