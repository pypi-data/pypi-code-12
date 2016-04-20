# yac variables are stored as:
# 
#{
#    "variable-name": {
#        "comment": "variable explanation",
#        "value":   "variable value"
#    }   
#}

def get_variable(params, variable_name, default_value="", value_key='value'):

    if variable_name in params and value_key in params[variable_name]:
        return params[variable_name][value_key]
    else:
        return default_value

def set_variable(params, variable_name, value, comment="", value_key='value'):

    params[variable_name] = {value_key : value, 'comment': comment}
    