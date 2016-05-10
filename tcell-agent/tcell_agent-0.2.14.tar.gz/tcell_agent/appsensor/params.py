# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

GET_PARAM = "get"
POST_PARAM = "post"
JSON_PARAM = "json"
COOKIE_PARAM = "cookies"

def test_param(param_name, param_value, test_func):
  if param_name is None or param_value is None:
    return None
  if isinstance(param_value, dict):
    for new_param_name in param_value:
      result = test_param(new_param_name, param_value[new_param_name], test_func)
      if result:
        return result
  elif isinstance(param_value, list):
    for new_param_value in param_value:
      result = test_param(param_name, new_param_value, test_func)
      if result:
        return result
  else:
    if isinstance(param_value, bytes):
      param_value = param_value.decode('utf-8')
    param_type = str(type(param_value))

    if(param_type == "<class 'str'>" or param_type == "<type 'str'>" or param_type == "<type 'unicode'>"):
      try:
        param_value = str(param_value)
        match = test_func(param_name, param_value)
        if match is not None:
            return match
      except:
        pass
  return None
