#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.exceptions  import ObjectDoesNotExist
from rest_framework.views    import exception_handler
from rest_framework.response import Response

class ModelWronglyDefined(Exception):
  pass

class WrongModelEstimationWorkflow(Exception):
  pass

class WrongDataLoading(Exception):
  pass

class PumpWoodException(Exception):
  pass

class PumpWoodUnauthorized(Exception):
  pass

class PumpWoodForbidden(Exception):
  pass

def SerializerException(exc):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    # Now add the HTTP status code to the response.
    if isinstance(exc, ModelWronglyDefined):
      return {'pk':None, 'model_class': 'Error', 'type': 'ModelWronglyDefined', 'msg': str(exc)}
      
    if isinstance(exc, WrongModelEstimationWorkflow):
      return {'pk':None, 'model_class': 'Error' ,'type': 'WrongModelEstimationWorkflow', 'msg': str(exc)}

    if isinstance(exc, WrongDataLoading):
      return {'pk':None, 'model_class': 'Error' ,'type': 'WrongDataLoading', 'msg': str(exc)}

    if isinstance(exc, PumpWoodException):
      return {'pk':None, 'model_class': 'Error' ,'type': 'PumpWoodException', 'msg': str(exc)}

    if isinstance(exc, ObjectDoesNotExist):
      return {'pk':None, 'model_class': 'Error' ,'type': 'ObjectDoesNotExist', 'msg': str(exc)}

    if isinstance(exc, PumpWoodUnauthorized):
      return {'pk':None, 'model_class': 'Error' ,'type': 'PumpWoodUnauthorized', 'msg': str(exc)}

    if isinstance(exc, PumpWoodForbidden):
      return {'pk':None, 'model_class': 'Error' ,'type': 'PumpWoodForbidden', 'msg': str(exc)}

    return None


def ExceptionRestHANDLER(exc, context):
  # serialized = SerializerException(exc)
  # if serialized:
  #   if isinstance(exc, PumpWoodUnauthorized):
  #     return Response(serialized, status=401)
    
  #   if isinstance(exc, PumpWoodForbidden):
  #     return Response(serialized, status=403)
    
  #   if isinstance(exc, ObjectDoesNotExist):
  #     return Response(serialized, status=404)

  #   return Response(serialized, status=400)
  # else:
    return exception_handler(exc, context)


exceptions_dict = {'PumpWoodUnauthorized':         PumpWoodUnauthorized
                 , 'ModelWronglyDefined':          ModelWronglyDefined
                 , 'WrongModelEstimationWorkflow': WrongModelEstimationWorkflow
                 , 'WrongDataLoading':             WrongDataLoading
                 , 'PumpWoodException':            PumpWoodException
                 , 'PumpWoodUnauthorized':         PumpWoodUnauthorized
                 , 'PumpWoodForbidden':            PumpWoodForbidden
                 , 'ObjectDoesNotExist':           ObjectDoesNotExist }