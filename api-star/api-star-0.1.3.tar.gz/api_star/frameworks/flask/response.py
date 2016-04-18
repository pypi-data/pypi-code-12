# coding: utf8
from __future__ import unicode_literals
from coreapi import Document
from flask import request, Response
from api_star.core import render


class APIResponse(Response):
    def __init__(self, data=None, *args, **kwargs):
        super(APIResponse, self).__init__(None, *args, **kwargs)
        (content, content_type) = render(request, data)
        self.set_data(content)
        if content_type:
            self.headers['Content-Type'] = content_type

    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (Document, list, dict)):
            return cls(response)
        return Response.force_type(response, environ)
