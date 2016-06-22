# from functools import wraps
#
# from flask.app import Flask
#
# from schemagic.core import validate_against_schema
# from schemagic.web import service_registry
#
# app = Flask(__name__)
# register_fibonnacci_services = service_registry(app)
#
#
# def memo(fn):
#     _cache = {}
#     @wraps(fn)
#     def _f(*args):
#         try:
#             return _cache[args]
#         except KeyError:
#             _cache[args] = result = fn(*args)
#             return result
#         except TypeError:
#             return fn(*args)
#     _f.cache = _cache
#     return _f
#
# @memo
# def fib(n):
#     if n == 0 or n == 1:
#         return 1
#     else:
#         return fib(n - 1) + fib(n - 2)
#
# register_fibonnacci_services(
#     dict(rule="/fibonacci",
#          input_schema={"n": int},
#          output_schema=int,
#          fn=fib))
#
# if __name__ == '__main__':
#     validate_against_schema({"n": int}, {"n": 6})
#     app.run(port=5000)
from schemagic.core import validate_against_schema
from schemagic.validators import null

validate_against_schema(null, "hello")
