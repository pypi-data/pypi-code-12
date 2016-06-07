from flask import jsonify as _jsonify


def jsonify(d):
    resp = _jsonify(d)
    resp.status_code = d.get("code", 200)
    return resp


def ok(ret=None):
    return jsonify({
        "code": 200,
        "msg": "OK",
        "result": ret
    })


def not_found(ret=None):
    return jsonify({
        "code": 404,
        "msg": "Not Found",
        "result": ret
    })


def bad_request(ret=None):
    return jsonify({
        "code": 400,
        "msg": "Bad Request",
        "result": ret
    })


def forbidden(ret=None):
    return jsonify({
        "code": 403,
        "msg": "Forbidden",
        "result": ret

    })


def server_error(ret=None):
    return jsonify({
        "code": 500,
        "msg": "Server Error",
        "result": ret
    })


def not_allowd(ret=None):
    return "Method not allowd", 405
