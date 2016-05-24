#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json

from django.core.exceptions import ObjectDoesNotExist
from .exceptions            import exceptions_dict\
                                 , PumpWoodUnauthorized\
                                 , ModelWronglyDefined\
                                 , WrongModelEstimationWorkflow\
                                 , WrongDataLoading\
                                 , PumpWoodException\
                                 , PumpWoodUnauthorized\
                                 , PumpWoodForbidden

class PumpWoodMicroService():
  '''
    :param microservice_name: Name of the microservice, helps when exceptions are raised
    :type microservice_name: str
    :param server_url: url of the server that will be connected
    :type server_url: str
    :param user_name: Username that will be logged on.
    :type user_name: str
    :param password: Variable to be converted to JSON and posted along with the request
    :type password: str
    :param local: Boolean if the service is to be considered local so have no conections with other PumpWoods
    :type local: bool

    Class to define an inter-pumpwood MicroService
  '''
  def __init__(self, microservice_name='', server_url=None, user_name=None, password=None, local=False):
    if server_url is None and user_name is None and password is None and local == True:
      self.user_name       = user_name
      self.password        = password
      self.server_url      = server_url
      self.request_session = None
      self.local = local
      self.microservice_name = microservice_name

    elif server_url is not None and user_name is not None and password is not None and local == False:
      self.user_name       = user_name
      self.password        = password
      self.server_url      = server_url
      self.request_session = None
      self.local = local
      self.microservice_name = microservice_name

    else:
      raise PumpWoodException('MicroService {name} miss-configured. For local, server_url, user_name, password must be None'.format(name=microservice_name))
    
  def raise_if_local(self):
    if self.local:
      raise PumpWoodException('MicroService {name} is working as local, so no connection can be stabilised.'.format(name=self.microservice_name))


  def error_handler(cls, response):
    if (response.status_code / 100) != 2:
      response_dict = PumpWoodMicroService.angular_json(response)
      raise exceptions_dict[response_dict['type']]( response_dict['msg'] )

  @staticmethod
  def angular_json(request_result):
    return (json.loads(request_result.text[6:]))

  def login(self):
    self.raise_if_local()

    self.request_session = requests.Session()
    self.request_session.headers.update({'Content-Type': 'application/json'})
    login_url = self.server_url + '/rest/registration/login/'

    login_result = self.request_session.post(login_url, data=json.dumps({'username': self.user_name, 'password': self.password}))
    login_data   = PumpWoodMicroService.angular_json(login_result)

    self.request_session.headers.update({'X-CSRFToken': login_data['csrf_token'], 'Authorization': 'Token ' + login_data['token']})

  def post(self, url, data):
    self.raise_if_local()

    if self.request_session is None:
      raise PumpWoodUnauthorized('MicroService {name} not looged'.format(name=self.microservice_name))
    
    post_url  = self.server_url + url
    post_data = json.dumps(data)

    response = self.request_session.post(url=post_url, data=post_data)
    self.error_handler(response)

    return PumpWoodMicroService.angular_json(response)

  def get(self, url):
    self.raise_if_local()

    if self.request_session is None:
      raise PumpWoodUnauthorized('MicroService {name} not looged'.format(name=self.microservice_name))
    
    post_url = self.server_url + url
    response = self.request_session.get(post_url)
    self.error_handler(response)

    return PumpWoodMicroService.angular_json(response)

  def default_pumpwood_services(self, model_class, end_point, type, args=None, post_data=None):
      '''
        :param model_class: Name of the class that will be requested
        :type model_class: str,
        :param type: Type of the request ("GET"/"POST")
        :type type: str,
        :param args: Args to be used in url creation
        :type args: str,int
        :param post_data: Variable to be converted to JSON and posted along with the request
        :type post_data: any

        Make a request to the deafult REST service at pumpwood.
      '''
      url_str = "/rest/" + model_class.lower() + "/" + end_point + "/"
      if end_point in ['retrieve']:
        url_str = url_str + str(args['pk']) + "/"

      if end_point in ['actions']:
        if type == 'post':
          url_str = url_str + args['action'] + '/' + str(args['pk']) + "/"

      if type == 'post':
        return self.post(url=url_str
                       , data=post_data)
      elif type == 'get':
        return self.get(url=url_str)
      else:
        raise Exception('Wrong type:', type)