# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import request, jsonify


def make_error(status_code, message):
    response = jsonify({
        'status': status_code,
        'message': message,
        'action': request.path
    })
    response.status_code = status_code
    return response


def badrequesterror(message):
    return make_error(400, message)


def forbiddenerror(error_code, message):
    return make_error(403, message)


def notfounderror(message='Taget not found!'):
    return make_error(404, message)


def methodnotallowed(message):
    return make_error(405, message)


def internalservererror(error_code, message):
    return make_error(500, message)
