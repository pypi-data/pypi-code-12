__author__ = 'schlitzer'

from bottle import Bottle, request, response


# index and document id´s should not start with an underscore
# this is not explicit forbidden by elasticsearch,
# but not recommended, but we do not allow it here.
str_index = '/<_index:re:[a-zA-Z0-9\.]{1}[a-zA-Z0-9_\-\.,]*>'
str_id = '<_id:re:[a-zA-Z0-9\.]{1}[a-zA-Z0-9_\-\.]*>'
#str_index = '/<_index:re:(?!_)>'
#str_id = '<_id:re:(?!_)>'

app = Bottle()


