from datetime import datetime, timedelta
from flask_restful import reqparse
from Param import Param
from ..DateTimeEncoder.DateTimeEncoder import DateTimeEncoder


def get_parameters(
    request_args= None,
    params= None,
    prefix=None
):
    if request_args is None:
        raise ValueError('The Flask-RESTful request arguments must be passed.')
#    if not isinstance(type(request_args), type(reqparse)):
#        raise TypeError('The request context is not of type flask_restful.reqparse')

    if params is None:
        return

    return_dict = {}

    t_params = (param for param in params if isinstance(param, Param))
    for param in t_params:
        param.value = request_args.get(param.parameter_name)
        if param.value is not None:
            if param.parameter_type == datetime:
                if param.value.lower() in ('today', 'now', ''):
                    param.value = datetime.utcnow()
                elif param.value.lower() in ('yesterday'):
                    param.value = datetime.utcnow() - timedelta(days=1)
                elif param.value.lower() in ('lastweek', 'last week', 'last-week'):
                    param.value = datetime.utcnow() - timedelta(days=7)
                else:
                    param.value = DateTimeEncoder.string_time_decode(str(param.value))
                if not isinstance(param.value, datetime):
                    raise TypeError('{0} is not a valid date.'.format(param.parameter_name))
            elif param.parameter_type == int:
                if param.value == '':
                    param.value = 0
                param.value = int(param.value)
            elif param.parameter_type == float:
                if param.value == '':
                    param.value = 0
                param.value = float(param.value)
        else:
            if param.parameter_default is not None:
                param.value = param.parameter_default
            elif param.parameter_required:
                raise ValueError('{0} not provided.'.format(param.parameter_name))

        if prefix is not None:
            _parameter_name = prefix + param.p_name
        else:
            _parameter_name = param.p_name
        return_dict[_parameter_name] = param.value

    return return_dict
