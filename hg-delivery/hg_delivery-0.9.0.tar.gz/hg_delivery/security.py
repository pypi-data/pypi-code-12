#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under the
# terms of the M.I.T License.
#
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.security import remember, forget, Allow, Everyone, Authenticated, unauthenticated_userid

from .models import (
    User,
    Acl, 
    Group,
    DBSession,
    Project,
    Task,
    )

GROUPS = {}
DEFAULT_USER = {}

#------------------------------------------------------------------------------

def get_user(request):
  """
  """
  userid = unauthenticated_userid(request)
  user = None
  if userid is not None:
    user = DBSession.query(User).filter(User.email==userid).scalar()

  return user

#------------------------------------------------------------------------------

def get_users():
  """
    return all known users from database
  """
  db_result = {email:password for (email,password) in DBSession.query(User.email,User.pwd)}
  # add default user
  db_result.update(DEFAULT_USER)
  return db_result

#------------------------------------------------------------------------------

def groupfinder(userid, request):
  result = None

  user = request.user
  if user is not None :
    result = GROUPS.get(user.email,['group:editors'])

  # whatever every body is an editor
  return ['group:editors']

#------------------------------------------------------------------------------

class RootFactory(object):
  """
  The default root factory.
  """
  
  __acl__ = [ (Allow, Everyone, 'view'),
              (Allow, 'group:editors', 'edit'),
              (Allow, 'group:editors', 'authenticated'),
              (Allow, Authenticated, 'authenticated')]

  def __init__(self, request):
    """
    """
    pass

#------------------------------------------------------------------------------

class ProjectFactory(object):
  """
    Specific factory for all Project object
  """

  def __init__(self, request):
    """
      For some routes, especially for project routes,
      we overwrite default root factory to serve specific
      acl coming from database instead of default and static ones ...

      Maybe it could be a better idea to test group and linked ACL
      instead of testing only default user ...
    """
    self.__acl__ = []

    self.request = request
    request.acl_container = self 

    id_user = request.authenticated_userid

    # we check if user is administrator (for the moment it's only configuration that drive this test)
    if request.registry.settings['hg_delivery.default_login'] == id_user :
      # shoud I link this to 'group:editors' instead of Authenticated ?
      self.__acl__ = [(Allow, Authenticated, 'edit'), (Allow, Authenticated, 'read')]
    else :
      self.__acl__ = self.get_acl()

  def get_acl(self):
    """
    """
    lst_acl = []
    # because of predicates id should be an int ...
    id_project = self.request.matchdict.get(u'id')
    if id_project is not None and self.request.user and self.request.user.id is not None :
      for (_label_acl,) in DBSession.query(Acl.acl).join(User).filter(Acl.id_project==id_project).filter(User.id==self.request.user.id) :
        # shoud I link this to 'group:editors' instead of Authenticated ?
        lst_acl.append((Allow, Authenticated, _label_acl))
        if _label_acl == 'edit' :
          lst_acl.append((Allow, Authenticated, 'read'))
    return lst_acl


  def contains(self, label_acl):
    """
    :param label_acl: label_acl
    """
    result = False
    if (Allow, Authenticated, label_acl) in self.__acl__ :
      result = True
    return result

#------------------------------------------------------------------------------

class TaskFactory(ProjectFactory):
  """
    Specific factory for all Task object
  """

  def get_acl(self):
    """
    """
    # because of predicates id should be an int ...
    id_task = self.request.matchdict[u'id']
    id_project = DBSession.query(Project.id).join(Task).filter(Task.id==id_task).scalar()
    lst_acl = []
    for (_label_acl,) in DBSession.query(Acl.acl).join(User).filter(Acl.id_project==id_project).filter(User.id==self.request.user.id) :
      # shoud I link this to 'group:editors' instead of Authenticated ?
      lst_acl.append((Allow, Authenticated, _label_acl))
      if _label_acl == 'edit' :
        lst_acl.append((Allow, Authenticated, 'read'))
    return lst_acl

#------------------------------------------------------------------------------

@view_config(route_name='login')
def login(request):
  login_url = request.route_url('login')
  referrer  = request.url

  if referrer == login_url:
      referrer = '/'  # never use login form itself as came_from

  came_from = request.params.get('came_from', referrer)
  message   = ''
  login     = ''
  password  = ''

  if 'login' in request.params and 'password' in request.params :
    login = request.params['login']
    password = request.params['password']
    all_known_users =  get_users()
    if login and password and all_known_users.get(login) == password:
        headers = remember(request, login)
        return HTTPFound( location = came_from,
                          headers  = headers )
    message = 'Failed login'

  return HTTPFound(location=request.route_url('home'))

#------------------------------------------------------------------------------

@view_config(route_name='logout')
def logout(request):
  headers = forget(request)
  url = request.route_url('home')

  return HTTPFound( location = url,
                    headers  = headers )
