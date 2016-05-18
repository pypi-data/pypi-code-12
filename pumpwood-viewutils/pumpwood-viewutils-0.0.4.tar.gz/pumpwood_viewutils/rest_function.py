#!/usr/bin/python
# -*- coding: utf-8 -*-
import inspect
from pumpwood_communication.exceptions import PumpWoodException

from django.core.exceptions import ImproperlyConfigured
from .serializers           import SerializerObjectActions

class RestAction:
  '''
    :param fn function: Function to extract name and class
    :param icon string: Icon that will be served to front end
    :param description string: String to describe action in front-end
    :param validation_dict dict: A dictionary to validate the post from the front
    :param many boolean: Tell if the fucntion is to be applied over many objects or only over one
    :param parameters dict: A dictionary containing the description of the parameters necessary to run the fucntion
    :param opt_parameters dict: A dictionary containing the description of the optional parameters to run the fucntion
    :param return_dict dict: A dictionary containing the description of what the function will return
    :param request_user string: A string telling if the request user will be used as as argument in function. None no, a string name of the kwargs key that will hold user name
     Classe que guarda as intruções para rodar as funções que serão disponibilizadas por rest
  '''

  def __init__(self, fn, model_class, icon, description, validation_dict, static, parameters, opt_parameters, return_dict, request_user=None):
    def check_parameter_dict(par_dict, transformation_dict, error_name):
      for k in par_dict.keys():
        if not set(par_dict[k].keys()) == set(['type', 'many']):
          raise KeyError('{function_name}: Transformation dict {error_name} entry {par_dict_key} does not have type and many keys'.format(function_name=fn.__name__, error_name=error_name, par_dict_key=k))

        if par_dict[k]['type'] not in transformation_dict:
          raise KeyError('{function_name}: Transformation dict {error_name} type entry {par_dict_key} does not have {trans_key} transformation'.format(function_name=fn.__name__, error_name=error_name, par_dict_key=k, trans_key=par_dict[k]['type']))
        
        if type(par_dict[k]['many']) != bool:
          raise TypeError('{function_name}: Transformation dict {error_name} type entry {par_dict_key} many is not bool'.format(function_name=fn.__name__, error_name=error_name, par_dict_key=k))

    args_in_function_original = inspect.getargspec(fn).args
    args_in_function          = []
    for i in range(0, len(args_in_function_original)):
      if args_in_function_original[i] not in ['self', 'cls', request_user]:
        args_in_function.append( args_in_function_original[i] )
    
    if set(args_in_function) != set( list(parameters.keys()) + list(opt_parameters.keys()) ):
      not_in_dicts = set(args_in_function) - set( list(parameters.keys()) + list(opt_parameters.keys()) )
      not_in_fun   = set( list(parameters.keys()) + list(opt_parameters.keys()) ) - set(args_in_function)
      raise Exception('Function {function_name} arguments and parameters + opt_parameters keys are not the same:\nArgs not in dicts: {not_in_dicts};\nArgs not in function pars: {not_in_fun}'.format(function_name=fn.__name__, not_in_dicts=not_in_dicts, not_in_fun=not_in_fun))


    self.icon            = icon
    self.modelclass      = model_class
    self.action_name     = fn.__name__
    self.description     = description
    self.validation_dict = validation_dict
    self.parameters      = parameters
    self.opt_parameters  = opt_parameters
    self.return_dict     = return_dict
    self.static          = static
    self.request_user    = request_user


class SerializerDictionary():
  __serializer_in_dict  = {}
  __serializer_out_dict = {}

  @classmethod
  def add_serializer_in(cls, var_type, one_lambda, many_lambda):
    cls.__serializer_in_dict[var_type] = {'one_lambda': one_lambda, 'many_lambda': many_lambda}

  @classmethod
  def add_serializer_out(cls, var_type, one_lambda, many_lambda):
    cls.__serializer_out_dict[var_type] = {'one_lambda': one_lambda, 'many_lambda': many_lambda}    

  @classmethod
  def check_in_type(cls, var_type):
    serializer = cls.__serializer_in_dict.get(var_type, None)
    return serializer is None

  @classmethod
  def check_out_type(cls, var_type):
    serializer = cls.__serializer_out_dict.get(var_type, None)
    return serializer is None

  @classmethod
  def serialize_in(cls, var_type, data):
    serializer = None
    if type(data) == list:
      serializer = cls.__serializer_in_dict.get(var_type, {}).get('many_lambda', None)
    else:
      serializer = cls.__serializer_in_dict.get(var_type, {}).get('one_lambda', None)

    if serializer is None:
      raise ImproperlyConfigured( 'It is not possible to find serializer to input ' + var_type )

    return serializer(data)

  @classmethod
  def serialize_out(cls, var_type, data):
    serializer = None
    if type(data) == list:
      serializer = cls.__serializer_out_dict.get(var_type, {}).get('many_lambda', None)
    else:
      serializer = cls.__serializer_out_dict.get(var_type, {}).get('one_lambda', None)
    
    if serializer is None:
      raise PumpWoodException( 'It is not possible to find serializer to output ' + var_type )

    return serializer(data)


class RestFunctionSerializer(object):
  @classmethod
  def run_rest_function(cls, function, request):
    action_obj = function.action_obj
    function_kwargs = cls.fun_args_parser(action_obj=action_obj, request=request)

    print 'function_kwargs: ', function_kwargs

    # if obj is not None:
    #   if action_obj.static:
    #     raise PumpWoodException('Static action being applied over an object.')
    # else:
    #   if not action_obj.static:
    #     raise PumpWoodException('Non-static action without an object being specified.')

    print 'function_kwargs__2: ', function_kwargs
    resp = function(**function_kwargs)
    return cls.result_parser(action_obj=action_obj, results=resp)


  @staticmethod
  def fun_args_parser(action_obj, request):
    '''
      Transforma o vetor de parâmetros dos actions nas variáveis adequadas
      Retira os parâmetros do dicionário action_parameters do próprio request
    '''
    parameter_dict = request.data

    response_dict = {}
    action_pars__keys     = action_obj.parameters.keys()
    opt_action_pars__keys = action_obj.opt_parameters.keys()
    parameter_dict__keys  = parameter_dict.keys()

    have_all_needed = list((set(action_pars__keys) - set(parameter_dict__keys)) - set(opt_action_pars__keys) )
    have_extra      = list(set(action_pars__keys) - set(parameter_dict__keys + opt_action_pars__keys))

    pump_text  = ""
    raise_pump = False
    if len(have_all_needed) != 0:
      joined = ", ".join(have_all_needed)
      pump_text = "Parameter missing to perform action: " + joined + "\n"
      raise_pump = True

    if len(have_extra) > 0:
      joined = ", ".join(have_extra)
      pump_text  = "More parameters needed then necessary to perform action: " + joined + "\n"
      raise_pump = True

    if raise_pump:
      raise PumpWoodException(pump_text)

    for k in parameter_dict.keys():
      if k in action_pars__keys:
        var_type = action_obj.parameters[k]['type']
        many     = action_obj.parameters[k]['many']
      else:
        var_type = action_obj.opt_parameters[k]['type']
        many     = action_obj.opt_parameters[k]['many']

      response_dict[k] = SerializerDictionary.serialize_in(var_type=var_type, data=parameter_dict[k])

    if action_obj.request_user is not None:
     response_dict[action_obj.request_user] = request.user
    
    return response_dict

  @staticmethod
  def result_parser(action_obj, results):
    '''
      Transforma os resultados em parâmetros serializados
    '''
    type_obj_result     = type(results)
    action_keys         = action_obj.return_dict.keys()

    to_return = None
    if type_obj_result == dict:
      #Resposta da função como um dicionário
      to_return = {}

      obj_result_keys = results.keys()
      have_all_needed  = list(set(action_keys) - set(obj_result_keys))
      if have_all_needed != []:
        raise TypeError('Keys in action result dict and not in object result: ' + str(have_all_needed))

      more_than_needed = list(set(obj_result_keys) - set(action_keys))
      if more_than_needed != []:
        raise TypeError('Keys in object result and not in action result dict: ' + str(more_than_needed))

      for obj_k in obj_result_keys:
        var_type = action_obj.return_dict[obj_k]['type']
        many = action_obj.return_dict[obj_k]['many']
        to_return[ obj_k ] = SerializerDictionary.serialize_out(var_type=var_type, data=results[obj_k])

    else:
      if len( action_keys ) > 1:
        raise TypeError('More than one key in action return dict and function return is not a dict.')

      if action_keys[0] != 'flat':
        raise TypeError('Result type not dict and return_dict dict with one key but not "flat"')

      var_type = action_obj.return_dict[ action_keys[0] ]['type']
      to_return = SerializerDictionary.serialize_out(var_type=var_type, data=results)

    return to_return



def rest_function(model_class, icon, description, validation_dict, static, parameters, opt_parameters, return_dict, request_user=None):
  def wrap(f):
    f.rest_function = True
    f.action_obj = RestAction(fn              = f
                            , model_class     = model_class
                            , icon            = icon
                            , description     = description
                            , validation_dict = validation_dict
                            , static          = static
                            , parameters      = parameters
                            , opt_parameters  = opt_parameters
                            , return_dict     = return_dict
                            , request_user    = request_user)
    return f
  return wrap