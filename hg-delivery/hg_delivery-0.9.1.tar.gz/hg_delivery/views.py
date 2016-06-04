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

from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import joinedload
from collections import OrderedDict

from threading import Thread, Event

from .models import (
    DBSession,
    Project,
    RemoteLog,
    User,
    Acl,
    Task,
    Group,
    Macro,
    MacroRelations,
    )

from hg_delivery.nodes import (
    NodeException,
    HgNewBranchForbidden,
    HgNewHeadsForbidden,
    NodeController,
    OutputErrorCode,
    OutputError,
    )

import paramiko
import logging

logging.getLogger("paramiko").setLevel(logging.WARNING)

import time
import logging
import re 

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------

class SpeedThread(Thread):

  def __init__(self, project, rev):
    """
    we're looking for a project and targeting a specific revision

    :param project: an sqlalchemy models.Project instance
    :param rev: a string hash revision
    """
    self.project     = project
    self.rev         = rev
    self._is_stopped = Event()

  def is_stopped(self):
    return self._is_stopped.is_set()

#------------------------------------------------------------------------------

class SpeedCrawler(SpeedThread):
  """
    a simple way to divide node jobs
  """

  def __init__(self, project, rev):
    """
    we're looking for a project and targeting a specific revision

    :param project: an sqlalchemy models.Project instance
    :param rev: a string hash revision
    """
    self.__linked     = False
    SpeedThread.__init__(self, project, rev)

  def start(self) :
    """
    Unleashed the dogs
    """
    try :
      # we check if this project has got this revision ...
      with NodeController(self.project) as ssh_node :
        node = ssh_node.get_revision_description(self.rev)
        if node is not None and 'rev' in node :
          self.__linked = True 
    except Exception as e:
      self.__linked = False

    self._is_stopped.set()

  def is_linked(self):
    return self.__linked

#------------------------------------------------------------------------------

class SpeedUpdater(SpeedThread):
  """
    a simple way to divide node jobs
  """

  def __init__(self, project, rev):
    """
    we're looking for a project and targeting a specific revision

    :param project: an sqlalchemy models.Project instance
    :param rev: a string hash revision
    """
    self.__updated          = False
    self.__tasks_exceptions = []

    SpeedThread.__init__(self, project, rev)

  def start(self) :
    """
      update a project to a specific revision (a hash)
    """
    try :
      with NodeController(self.project, silent=False) as ssh_node:
        ssh_node.update_to(self.rev)
        current_rev = ssh_node.get_current_rev_hash()
        stop_at = 0
        while current_rev!=self.rev and stop_at<10 :
          # sleep 100 ms
          time.sleep(0.100)
          current_rev = ssh_node.get_current_rev_hash()
          stop_at += 1

        if current_rev == self.rev :
          self.__updated = True

          for task in self.project.tasks :
            try :
              ssh_node.run_command(task.content, log=True)
            except NodeException as e :
              self.__tasks_exceptions.append(e.value)
          
    except Exception as e:
      pass

    self._is_stopped.set()

  def get_tasks_exceptions(self):
    return self.__tasks_exceptions

  def project_updated(self):
    return self.__updated
#------------------------------------------------------------------------------

@view_config(route_name='user_update', renderer='json', permission='edit')
def update_user(request):
    """
    update user ...
    """
    user_id = request.matchdict['id']

    user = DBSession.query(User)\
                    .filter(User.id==user_id)\
                    .scalar()

    result = False

    if user is not None :

      try :
        for attribute in request.params :
          setattr(user, attribute, request.params[attribute])
        DBSession.flush()
        result = True
        explanation = u'This user : %s (%s) has been updated ...'%(request.params['name'], request.params['email'])
      except IntegrityError as e:
        DBSession.rollback()
        result = False
        explanation = u"You can't update this user, this email is already used (%s %s) ..."%(request.params['name'], request.params['email'])

    else :
      explanation = u"This user is unknown or has already been deleted"

    return {'result'      : result,
            'explanation' : explanation}

#------------------------------------------------------------------------------

@view_config(route_name='user_delete', renderer='json', permission='edit')
def delete_user(request):
    """
    delete user ...
    """
    user_id = request.matchdict['id']
    user = DBSession.query(User)\
                    .filter(User.id==user_id)\
                    .scalar()

    if user :
      DBSession.delete(user)

    return HTTPFound(location=request.route_url(route_name='users'))

#------------------------------------------------------------------------------

@view_config(route_name='user_get', renderer='json', permission='edit')
def get_user(request):
    """
    delete user ...
    """
    user_id = request.matchdict['id']
    user = DBSession.query(User)\
                    .filter(User.id==user_id)\
                    .scalar()
    result = True

    return {'result' : result,
            'user'   : user}

#------------------------------------------------------------------------------

@view_config(route_name='user_add', renderer='json', permission='edit')
def add_user(request):
    """
    manage users ...
    """
    result = False
    explanation = None

    name = request.params['name']
    email = request.params['email']
    password = request.params['pwd']

    # email is the key, and password cannot be empty
    if not name :
      explanation = u'Your user profile should contain a valid name'
      result = False
    elif not email or not re.match('[^@]+@[^@]+',email):
      explanation = u'Your user profile should contain a valid email'
      result = False
    elif not password:
      explanation = u"Your user profile musn't be empty"
      result = False
    else:
      try :
        # folder should be unique
        user = User(**request.params)
        DBSession.add(user)
        DBSession.flush()
        result = True
        explanation = u'This user : %s (%s) has been added ...'%(name, email)
      except IntegrityError as e:
        DBSession.rollback()
        result = False
        explanation = u'This user and this email are already defined (%s %s) ...'%(name, email)

    return { 'result'      : result,
             'explanation' : explanation }

#------------------------------------------------------------------------------

@view_config(route_name='users_json', renderer='json', permission='edit')
@view_config(route_name='users', renderer='templates/users.mako', permission='edit')
def manage_users(request):
    """
    manage users ...
    retrieve and publish user list and project list
    """
    lst_users = DBSession.query(User).all()
    project_acls = {}
    for _p in DBSession.query(Project) :
      project_acls[_p.id] = {_acl.id_user:_acl.acl for _acl in DBSession.query(Acl).filter(Acl.id_project == _p.id)}

    return {'lst_users':lst_users,
            'known_acls':Acl.known_acls,
            'project_acls':project_acls}

#------------------------------------------------------------------------------

@view_config(route_name='contact', renderer='templates/contact.mako')
def contact(request):
    """
    contact information
    """
    return {}

#------------------------------------------------------------------------------

@view_config(route_name='description', renderer='json', permission='authenticated')
def node_description(request):
  """
  return node description
  """
  id_project = request.matchdict['id']
  project = DBSession.query(Project).get(id_project)

  if not project.is_initial_revision_init() :
    project.init_initial_revision()

  node_description = {}

  try :
    with NodeController(project, silent=True) as ssh_node :
      repository_node = ssh_node.get_current_revision_description()

      current_rev = None
      if repository_node and 'node' in repository_node :
        current_rev = repository_node['node']
      node_description = repository_node
  except NodeException :
    # a paramiko error
    # linked to network error
    # File "....   venv/lib/python3.4/site-packages/paramiko-1.16.0-py3.4.egg/paramiko/ssh_exception.py", line 168, in __init__
    #   body = ', '.join([x[0] for x in addrs[:-1]])
    # TypeError: 'dict_keys' object is not subscriptable
    pass

  return { 'node_description':node_description }

#------------------------------------------------------------------------------

@view_config(route_name='home', renderer='templates/index.mako')
def default_view(request):
    """
    """
    dashboard_list = []
    nodes_description = {}
    projects_list = []

    if request.authenticated_userid :
      projects_list = []
      if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
        projects_list = DBSession.query(Project).order_by(Project.name.desc()).all()
      else :
        projects_list = DBSession.query(Project)\
                                 .join(Acl)\
                                 .join(User)\
                                 .filter(User.id==request.user.id)\
                                 .order_by(Project.name.desc())\
                                 .all()

      for project in projects_list :
        ssh_node = None
        try :
          if project.dashboard!=1 :
            continue

          dashboard_list.append(project)
          nodes_description[project.id] = {}

        except NodeException as e:
          nodes_description[project.id] = {}

    return { 'projects_list':projects_list,
             'nodes_description':nodes_description,
             'dashboard_list':dashboard_list,
           }

#------------------------------------------------------------------------------

@view_config(route_name='logs', renderer='json', permission='edit')
def logs(request):
    """
    fetch all logs
    """
    lst_logs = DBSession.query(RemoteLog)\
                        .order_by(RemoteLog.creation_date.desc())\
                        .limit(50)\
                        .all()
    return { 'logs': lst_logs}

#------------------------------------------------------------------------------

@view_config(route_name='project_logs', renderer='json', permission='edit')
def project_logs(request):
  """
  fetch logs linked to a project
  """
  id_project = request.matchdict['id']

  lst_logs = DBSession.query(RemoteLog)\
                      .filter(RemoteLog.id_project==id_project)\
                      .order_by(RemoteLog.creation_date.desc())\
                      .limit(50)\
                      .all()
  
  return { 'logs': lst_logs}

#------------------------------------------------------------------------------

@view_config(route_name='project_push_test', renderer='json')
def shall_we_push(request):
  """
    test if push is available regarding to push query result
  """
  id_project = request.matchdict['id']
  id_target_project = request.matchdict['target']

  project = DBSession.query(Project).get(id_project)
  target_project = DBSession.query(Project).get(id_target_project)
  result = False
  if project and target_project :
    with NodeController(project, silent=True) as ssh_node :
      result = ssh_node.pushable(project, target_project)
  return {'result':result}

#------------------------------------------------------------------------------

@view_config(route_name='project_pull_test', renderer='json')
def shall_we_pull(request):
  """
    test if pull is available regarding to push query result
  """
  id_project = request.matchdict['id']
  id_target_project = request.matchdict['source']

  project = DBSession.query(Project).get(id_project)
  target_project = DBSession.query(Project).get(id_target_project)
  result = False
  if project and target_project :
    with NodeController(project, silent=True) as ssh_node :
      result = ssh_node.pullable(project, target_project)
  return {'result':result}

#------------------------------------------------------------------------------

@view_config(route_name='project_brothers', renderer='json')
def project_brothers(request):
  """
    check who is sharing this project
  """
  id_project = request.matchdict['id']

  project = DBSession.query(Project).get(id_project)
  projects_list = []

  if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
    projects_list = DBSession.query(Project)\
                             .order_by(Project.name.desc())\
                             .all()
  else :
    projects_list = DBSession.query(Project)\
                             .join(Acl)\
                             .join(User)\
                             .filter(User.id==request.user.id)\
                             .order_by(Project.name.desc())\
                             .all()

  linked_projects = [p for p in projects_list if p.rev_init is not None and p.rev_init == project.rev_init and p.id != project.id]
  return {'brothers':linked_projects}

#------------------------------------------------------------------------------

@view_config(route_name='project_brothers_update_check', renderer='json')
def who_share_this_id(request):
  """
    check who is sharing this id
  """
  id_project = request.matchdict['id']
  rev = request.matchdict['rev']

  project = DBSession.query(Project).get(id_project)
  projects_list = []

  if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
    projects_list = DBSession.query(Project)\
                             .order_by(Project.name.desc())\
                             .all()
  else :
    projects_list = DBSession.query(Project)\
                             .join(Acl)\
                             .filter(Acl.acl=='edit')\
                             .join(User)\
                             .filter(User.id==request.user.id)\
                             .order_by(Project.name.desc())\
                             .all()

  linked_projects = [p for p in projects_list if p.rev_init is not None and p.rev_init == project.rev_init and p.id != project.id and not p.no_scan]
  thread_stack    = []

  for __p in linked_projects:
    new_thread = SpeedCrawler(__p, rev)
    thread_stack.append(new_thread)
    new_thread.start()

  t0 = time.time()
  while sum([e.is_stopped() for e in thread_stack])!=len(linked_projects) or time.time()>(t0+10*60):
    time.sleep(0.005)

  # when threads finished their job
  # we filter linked projects
  projects_sharing_that_rev = [c.project for c in thread_stack if c.is_linked()]

  # found linked projects
  return {'projects_sharing_that_rev':projects_sharing_that_rev}

#------------------------------------------------------------------------------

@view_config(route_name='macro_fetch', renderer='json', permission='edit')
def edit_a_macro(request):
  """
  """
  result = False
  project_id = request.matchdict['id']
  macro_id   = request.matchdict['macro_id']

  macro = DBSession.query(Macro).options(joinedload(Macro.relations)).get(macro_id)
  macro_relations = macro.relations

  map_relations = {}

  if macro_relations is not None and len(macro_relations)>0:
    for relation in macro_relations :
      direction                       = relation.direction
      id_third_project                = relation.id_third_project
      map_relations[id_third_project] = direction
    result = True
  else :
    result = False
  return {'result':result, 'map_relations':map_relations, 'label':macro.label}

#------------------------------------------------------------------------------

@view_config(route_name='macros', renderer='templates/macros.mako', permission='edit')
def view_all_macros(request):
  """
  """
  if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
    macros = DBSession.query(Macro).join(Project).options(joinedload(Macro.relations)).order_by(Project.name.desc()).all()
  else :
    macros = DBSession.query(Macro).join(Project).join(Acl).filter(Acl.acl=='edit').join(User).filter(User.id==request.user.id).options(joinedload(Macro.relations)).order_by(Project.name.desc()).all()

  dict_project_to_macros = OrderedDict()

  for macro in macros :
    project = macro.project
    if project in dict_project_to_macros :
      dict_project_to_macros[project].append(macro)
    else :
      dict_project_to_macros[project] = [macro]
  return {'dict_project_to_macros':dict_project_to_macros}

#------------------------------------------------------------------------------

@view_config(route_name='macro_refresh', renderer='templates/edit#publish_project_macros.mako', permission='edit')
def refresh_macros(request):
  """
    re-publish the list of macros ....
  """
  id_project = request.matchdict['id']
  project    = DBSession.query(Project).get(id_project)

  project_macros = DBSession.query(Macro).filter(Macro.id_project == id_project).all()

  if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
    projects_list = DBSession.query(Project)\
                             .order_by(Project.name.desc())\
                             .all()
  else :
    projects_list = DBSession.query(Project)\
                             .join(Acl)\
                             .filter(Acl.acl=='edit')\
                             .join(User)\
                             .filter(User.id==request.user.id)\
                             .order_by(Project.name.desc())\
                             .all()

  linked_projects = [p for p in projects_list if p.rev_init is not None and p.rev_init == project.rev_init and p.id != project.id]

  return {'project_macros'  : project_macros,
          'project'         : project,
          'linked_projects' : linked_projects}

#------------------------------------------------------------------------------

@view_config(route_name='macro_delete', renderer='json')
def delete_a_macro(request):
  """
    create a macro on a specific project.
    A macro is a list of bind project that shall be push or pull
  """
  result = False
  try :
    macro_id = request.matchdict['macro_id']
    macro = DBSession.query(Macro).get(macro_id)
    DBSession.delete(macro)
    DBSession.flush()
    result = True
  except :
    DBSession.rollback()
    result = False

  return {'result':result}

#------------------------------------------------------------------------------

@view_config(route_name='macro_update', renderer='json', permission='edit')
def update_a_macro(request):
  """
    update a specific macro on a specific project.
    A macro is a list of bind project that shall be push or pull
  """
  result      = False
  explanation = None
  id_project  = request.matchdict['id']
  macro_id    = request.matchdict['macro_id']
  macro       = DBSession.query(Macro).options(joinedload(Macro.relations)).get(macro_id)

  # a name is mandatory for the macro ...
  macro_name    = None
  if macro is not None and 'macro_name' in request.params :
    try :
      macro_name    = request.params['macro_name']
      macro_content = {}

      for _param in request.params :
        if re.match('^direction_[0-9]{1,}',_param) and request.params[_param] in {'push','pull'}:
          aim_id_project = _param.split('_')[1]
          aim_value      = request.params[_param]
          macro_content[aim_id_project] = aim_value

      if macro_name and len(macro_name)>1 and len(macro_content)>0 :
        macro.label = macro_name
        macro.relations[0:]=[]

        for _p_id in macro_content :
          macro_relation = MacroRelations(_p_id, macro_content[_p_id])
          DBSession.add(macro_relation)
          macro.relations.append(macro_relation)

        DBSession.flush()
        result = True
    except IntegrityError as e:
      DBSession.rollback()
      result = False
      explanation = u'This project and this path are already defined (%s %s) ...'%(host, path)

  return {'result':result, 'explanation':explanation}

#------------------------------------------------------------------------------
@view_config(route_name='macro_add', renderer='json', permission='edit')
def create_a_macro(request):
  """
    create a macro on a specific project.
    A macro is a list of bind project that shall be push or pull
  """
  id_project = request.matchdict['id']
  result     = False

  # a name is mandatory for the macro ...
  macro_name    = None
  if 'macro_name' in request.params :
    macro_name    = request.params['macro_name']

    macro_content = {}

    for _param in request.params :
      if re.match('^direction_[0-9]{1,}',_param) and request.params[_param] in {'push','pull'}:
        aim_id_project = _param.split('_')[1]
        aim_value      = request.params[_param]
        macro_content[aim_id_project] = aim_value

    if macro_name and len(macro_name)>1 and len(macro_content)>0 :

      macro = Macro(id_project, macro_name)
      DBSession.add(macro)

      for _p_id in macro_content :
        macro_relation = MacroRelations(_p_id, macro_content[_p_id])
        DBSession.add(macro_relation)
        macro.relations.append(macro_relation)

      DBSession.flush()
      result = True

  return {'result':result}

#------------------------------------------------------------------------------

@view_config(route_name='macro_run', renderer='json', permission='edit')
def run_a_macro(request):
  """
    Run a macro

    hum ... if push, could we push with thread ?
    shall we check to whom we need to push

    first ... : pull
    then  ....: all the push execution ...

  """
  result           = True
  new_branch_stop  = False
  new_head_stop    = False
  force_branch     = False
  lst_new_branches = []
  project_errors   = []
  buffers_output   = {}

  if 'force_branch' in request.params and request.params['force_branch']=='true':
    force_branch = True 

  id_project = request.matchdict['id']
  project    = DBSession.query(Project).get(id_project)

  macro_id = request.matchdict['macro_id']
  macro    = DBSession.query(Macro).options(joinedload(Macro.relations)).get(macro_id)


  projects_id_set = set()
  if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
    projects_id_set = {p.id for p in DBSession.query(Project).order_by(Project.name.desc())}
  else :
    projects_id_set = {p.id for p in DBSession.query(Project).join(Acl).filter(Acl.acl=='edit').join(User).filter(User.id==request.user.id).order_by(Project.name.desc())}

  for relation in macro.relations :

    aim_project = relation.aim_project

    # user must have an access to this project
    if aim_project.id not in projects_id_set :
      result = False 
      project_errors.append(aim_project.name)
      buffers_output[aim_project.name] = u"user don't have access to %s"%aim_project.name
      continue

    # if user don't have access to this project we just pass
    # because a macros is across several projects
    # it's meanless 

    # shall we display a macro if user has access to all projects
    # included the source project ...


    direction   = relation.direction
    __result    = True

    if project and aim_project and direction == 'push' :

      ssh_node        = None
      ssh_node_remote = None

      try :
        with NodeController(project) as ssh_node :
          data = ssh_node.push_to(project, aim_project, force_branch)
      except HgNewBranchForbidden as e:
        # we may inform user that he cannot push ...
        # maybe add a configuration parameter to fix this
        # and send --new-branch directly on the first time
        new_branch_stop = True
        __result        = False

        set_local_branches = set()
        with NodeController(project, silent=True) as ssh_node :
          set_local_branches = set(ssh_node.get_branches())

        try :
          with NodeController(aim_project) as ssh_node_remote :
            set_remote_branches = set(ssh_node_remote.get_branches())
            lst_new_branches = list(set_local_branches - set_remote_branches)
            data = e.value
        except :
          data = {}

        project_errors.append(aim_project.name)
      except HgNewHeadsForbidden as e:
        # we may inform user that he cannot push ...
        # maybe add a configuration parameter to fix this
        # and send --new-branch directly on the first time
        new_head_stop    = True
        __result         = False
        lst_new_branches = []
        buffers_output[aim_project.name] = e.value.get('buff')
        project_errors.append(aim_project.name)
      except (OutputErrorCode, OutputError) as e:
        # we may inform user that push has not finished correctly :/
        __result  = False
        project_errors.append(aim_project.name)
        buffers_output[aim_project.name] = e.value.get('buff')
      else :
        __result = True

    elif project and aim_project and direction == 'pull':

      with NodeController(project, silent=True) as ssh_node :
        ssh_node.pull_from(project, aim_project)
        __result = True

    result &= __result

  return {'new_branch_stop'  : new_branch_stop,
          'new_head_stop'    : new_head_stop,
          'lst_new_branches' : lst_new_branches,
          'project_errors'   : project_errors,
          'buffers'          : buffers_output,
          'result'           : result}

#------------------------------------------------------------------------------

@view_config(route_name='project_push_to', renderer='json', permission='edit')
def push(request):
  """
  """
  id_project = request.matchdict['id']
  id_target_project = request.matchdict['target']

  project = DBSession.query(Project).get(id_project)
  target_project = DBSession.query(Project).get(id_target_project)

  new_branch_stop = False
  new_head_stop = False
  result = False
  force_branch = False
  lst_new_branches = []
  data = {'buff':''}

  if project and target_project :

    if 'force_branch' in request.params and request.params['force_branch']=='true':
      force_branch = True 

    ssh_node = None
    ssh_node_remote = None

    try :
      with NodeController(project) as ssh_node :
        data = ssh_node.push_to(project, target_project, force_branch)
    except HgNewBranchForbidden as e:
      # we may inform user that he cannot push ...
      # maybe add a configuration parameter to fix this
      # and send --new-branch directly on the first time
      new_branch_stop = True
      result = False

      set_local_branches = set()
      with NodeController(project, silent=True) as ssh_node :
        set_local_branches = set(ssh_node.get_branches())

      try :
        with NodeController(target_project) as ssh_node_remote :
          set_remote_branches = set(ssh_node_remote.get_branches())
          lst_new_branches = list(set_local_branches - set_remote_branches)
          data = e.value
      except :
        data = {}
    except HgNewHeadsForbidden as e:
      # we may inform user that he cannot push ...
      # maybe add a configuration parameter to fix this
      # and send --new-branch directly on the first time
      new_head_stop = True
      result = False
      lst_new_branches = [] 
      data = e.value
    except (OutputErrorCode, OutputError) as e:
      # we may inform user that push has not finished correctly :/
      result = False
      data   = e.value
    else :
      result = True
  
  return {'new_branch_stop'  : new_branch_stop,
          'new_head_stop'    : new_head_stop,
          'lst_new_branches' : lst_new_branches,
          'buffer'           : data.get('buff'),
          'result'           : result}
#------------------------------------------------------------------------------

@view_config(route_name='project_pull_from', renderer='json', permission='edit')
def pull(request):
  """
  """
  id_project = request.matchdict['id']
  id_source_project = request.matchdict['source']

  project = DBSession.query(Project).get(id_project)
  source_project = DBSession.query(Project).get(id_source_project)

  with NodeController(project, silent=True) as ssh_node :
    ssh_node.pull_from(project, source_project)
  return {}

#------------------------------------------------------------------------------

@view_config(route_name='project_add', renderer='json', permission='edit')
def add_project(request):
    """
    create a new project
    """
    result = False
    explanation = None

    host = request.params['host']
    path = request.params['path']
    user = request.params['user']

    if not host :
      explanation = u'Your project should contain a valid hostname'
    elif not path :
      explanation = u'Your project should contain a valid path'
    else:
      try :
        # folder should be unique
        project = Project(**request.params)
        DBSession.add(project)
        DBSession.flush()
        project.init_initial_revision()
        result = True
        explanation = u'This project : %s@%s/%s has been added ...'%(user, host, path)
      except IntegrityError as e:
        DBSession.rollback()
        result = False
        explanation = u'This project and this path are already defined (%s %s) ...'%(host, path)

    return { 'result'      : result,
             'explanation' : explanation }

#------------------------------------------------------------------------------

@view_config(route_name='project_update', renderer='json', permission='edit')
def update_project(request):
    """
    update the project properties (host, path, password ...)
    """
    result = False
    id_project = request.matchdict['id']

    host = request.params['host']
    path = request.params['path']
    user = request.params['user']
    project = None
    explanation = None

    if not host :
      explanation = u'Your project should contain a valid hostname'
    elif not path :
      explanation = u'Your project should contain a valid path'
    else:
      try :
        project = DBSession.query(Project).get(id_project)
        for key in request.params :
          setattr(project, key, request.params[key])

        if 'dashboard' not in request.params :
          project.dashboard = 0

        DBSession.flush()
        explanation = u'This project : %s@%s/%s has been updated ...'%(user, host, path)
        result = True
      except :
        DBSession.rollback()
        result = False

    return { 'result'      : result,
             'project'     : project,
             'explanation' : explanation  }

#------------------------------------------------------------------------------

@view_config(route_name='view_file_content', permission='edit')
def get_file_content(request):
    """
    view file content regarding to revision id
    """
    id_project = request.matchdict['id']
    revision = request.matchdict['rev']
    file_name = "/".join(request.matchdict['file_name'])
    project = DBSession.query(Project).get(id_project)
    data = ""
    with NodeController(project, silent=True) as ssh_node :
      data = ssh_node.get_content(revision, file_name)
    response = Response(data)
    return response

#------------------------------------------------------------------------------

@view_config(route_name='project_delete', renderer='json', permission='edit')
def delete_project(request):
    """
    delete a project
    """
    result = False
    try :
      id_project = request.matchdict['id']
      project = DBSession.query(Project).get(id_project)
      project.delete_nodes()
      # also delete macros or relation that target that project

      DBSession.delete(project)
      DBSession.flush()
      result = True
    except :
      DBSession.rollback()
      result = False

    return { 'result':result }

#------------------------------------------------------------------------------

@view_config(route_name='project_refresh_state', renderer='json', permission='edit')
@view_config(route_name='project_edit', renderer='edit.mako', permission='read')
def edit_project(request):
    """
    """
    result = False
    id_project = request.matchdict['id']

    projects_list           = []
    projects_list_protected = []

    if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
      projects_list = DBSession.query(Project).order_by(Project.name.desc()).all()
      projects_list_protected = projects_list
    else :
      projects_list = DBSession.query(Project).join(Acl).join(User).filter(User.id==request.user.id).order_by(Project.name.desc()).all()
      projects_list_protected = DBSession.query(Project).join(Acl).filter(Acl.acl=='edit').join(User).filter(User.id==request.user.id).order_by(Project.name.desc()).all()

    projects_map = {p.id:p for p in projects_list}
    project = projects_map.get(id_project)

    if project is None :
      return HTTPFound(location=request.route_url(route_name='home'))

    if not project.is_initial_revision_init() :
      project.init_initial_revision()

    # while editing this project, we also check non inited projects
    # shall we ?
    # for p in projects_list :
    #   if not p.is_initial_revision_init() :
    #     p.init_initial_revision()

    delivered_hash = {}
    for l in DBSession.query(RemoteLog.command, RemoteLog.creation_date)\
                      .order_by(RemoteLog.creation_date.desc())\
                      .filter(RemoteLog.id_project==id_project)\
                      .filter(RemoteLog.command.like('%hg update -C -r%'))\
                      .limit(200) :
      if l.command.count('hg update -C -r') :
        hash_rev = l.command.split('hg update -C -r ')[1].strip()
        if hash_rev in delivered_hash :
          delivered_hash[hash_rev].append(l.creation_date.strftime('%d/%m/%Y %H:%M:%S'))
        else :
          delivered_hash[hash_rev] = [l.creation_date.strftime('%d/%m/%Y %H:%M:%S')]

    linked_projects = [p for p in projects_list_protected if p.rev_init is not None and p.rev_init == project.rev_init and p.id != project.id and p.is_initial_revision_init()]

    branch = None
    if 'branch' in request.params :
      branch = request.params['branch']

    tag = None
    if 'tag' in request.params :
      tag = request.params['tag']

    limit = 200 
    settings = request.registry.settings
    if 'hg_delivery.default_log_limit' in settings and settings['hg_delivery.default_log_limit'].isdigit():
      limit = int(settings['hg_delivery.default_log_limit'])

    request.registry.settings 
    if 'limit' in request.params and request.params['limit'].isdigit():
      limit = int(request.params['limit'])

    repository_error = None

    users = DBSession.query(User).all()

    project_acls   = {_acl.id_user:_acl.acl for _acl in DBSession.query(Acl).filter(Acl.id_project == id_project)}
    project_tasks  = DBSession.query(Task).filter(Task.id_project == id_project).all()
    project_macros = DBSession.query(Macro).filter(Macro.id_project == id_project).all()

    try :
      with NodeController(project) as ssh_node :

        if not project.dvcs_release :
          project.dvcs_release = ssh_node.get_release()

        current_rev = ssh_node.get_current_rev_hash()

        last_hundred_change_list, map_change_sets = ssh_node.get_last_logs(limit, branch_filter=branch, revision_filter=tag)
        list_branches = ssh_node.get_branches()
        list_tags = ssh_node.get_tags()

        current_node = map_change_sets.get(current_rev)
        if current_node is None :
          current_node = ssh_node.get_revision_description(current_rev)
    except NodeException as e:
      repository_error = e.value
      log.error(e.value)
      current_node = None
      list_branches = []
      list_tags = []
      last_hundred_change_list, map_change_sets = [], {}
    except OSError as e:
      repository_error = "Host seems not available. Fix this network issue"
      log.error("Host seems not available. Fix this network issue")
      current_node = None
      list_branches = []
      list_tags = []
      last_hundred_change_list, map_change_sets = [], {}
    except Exception as e:
      if hasattr(e,'value') :
        repository_error = e.value
        log.error(e.value)
      else :
        log.error(e)

      current_node = None
      list_branches = []
      list_tags = []
      last_hundred_change_list, map_change_sets = [], {}

    id_user = request.authenticated_userid
    allow_to_modify_acls = False
    if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
      allow_to_modify_acls = True

    for node in last_hundred_change_list :
      node['url_detail']                = request.route_url(route_name='project_revision_details_json',id=project.id, rev=node['node'])
      node['url_change_to']             = request.route_url('project_change_to',id=project.id, rev=node['node'], brother_id =[])
      node['url_refresh']               = request.route_url('project_refresh_state',id=project.id)
      node['url_brothers_update_check'] = request.route_url('project_brothers_update_check',id=project.id, rev=node['node'])

    return { 'project'                  : project,
             'list_branches'            : list_branches,
             'list_tags'                : list_tags,
             'limit'                    : limit,
             'projects_list'            : projects_list,
             'filter_tag'               : tag,
             'filter_branch'            : branch,
             'repository_error'         : repository_error,
             'current_node'             : current_node,
             'linked_projects'          : linked_projects,
             'last_hundred_change_list' : last_hundred_change_list,
             'users'                    : users,
             'allow_to_modify_acls'     : allow_to_modify_acls,
             'project_acls'             : project_acls,
             'project_tasks'            : project_tasks,
             'project_macros'           : project_macros,
             'knonwn_acl'               : Acl.known_acls,
             'delivered_hash'           : delivered_hash}

#------------------------------------------------------------------------------

@view_config(route_name='project_run_task', renderer='json', permission='edit')
def run_task(request):
  """
  """
  id_task     = request.matchdict['id']
  task        = DBSession.query(Task).get(id_task)
  result      = False
  explanation = u""

  if task :
    try :
      with NodeController(task.project) as ssh_node :
        ssh_node.run_command(task.content, log=True)
    except NodeException as e:
      result = False
      explanation = e.value
    except IntegrityError as e:
      result = False
      explanation = u"wtf ?"
    else :
      result = True 

  return {'result':result, 'explanation':explanation}

#------------------------------------------------------------------------------

@view_config(route_name='tasks', renderer='templates/tasks.mako', permission='edit')
def view_all_tasks(request):
  """
  """
  if request.registry.settings['hg_delivery.default_login'] == request.authenticated_userid :
    tasks = DBSession.query(Task).join(Project).options(joinedload(Task.project)).order_by(Project.name.desc()).all()
  else :
    tasks = DBSession.query(Task).join(Project).join(Acl).filter(Acl.acl=='edit').join(User).filter(User.id==request.user.id).options(joinedload(Task.project)).order_by(Project.name.desc()).all()

  dict_project_to_tasks = OrderedDict()

  for task in tasks :
    project = task.project
    if project in dict_project_to_tasks :
      dict_project_to_tasks[project].append(task)
    else :
      dict_project_to_tasks[project] = [task]

  return {'dict_project_to_tasks':dict_project_to_tasks}

#------------------------------------------------------------------------------

@view_config(route_name='project_delete_task', renderer='json', permission='edit')
def remove_project_task(request):
  """
    remove some task on project
  """
  id_task = request.matchdict['id']
  result = False
  try :
    task = DBSession.query(Task).get(id_task)
    DBSession.delete(task)
  except IntegrityError as e:
    result = False
    explanation = u"wtf ?"
  else :
    result = True 

  return {'result':result}

#------------------------------------------------------------------------------

@view_config(route_name='project_save_tasks', renderer='json', permission='edit')
def save_project_tasks(request):
  """
  """
  id_project = request.matchdict['id']
  project = DBSession.query(Project).get(id_project)
  result = False

  if project :
    try :
      # we remove old tasks 
      project.tasks[0:] = []
      for  _task_content in request.params.getall('task_content') :
        if _task_content :
          task = Task(id_project, _task_content.strip())
          # make the link with DBSession ...
          DBSession.add(task)
          project.tasks.append(task)
      DBSession.flush()
      result = True
    except IntegrityError as e:
      DBSession.rollback()
      result = False
      explanation = u"wtf ?"

  return {'result':result, 'tasks':project.tasks}

#------------------------------------------------------------------------------

@view_config(route_name='user_acls', renderer='json', permission='edit')
def get_user_acls(request):
  """
  """
  id_user = request.matchdict['id']
  user = DBSession.query(User).get(id_user)

  result = False
  acls   = []

  if user :
    result = True
    acls = user.acls
  return {'result':result, 'acls':acls, 'known_acls':Acl.known_acls}

#------------------------------------------------------------------------------

@view_config(route_name='users_save_acls', renderer='json', permission='edit')
def save_users_acls(request):
  """
  """

  result = False

  map_project_users_ace = {}

  try :
    for ele, _acl_label in request.params.iteritems() :
      id_project, id_user = (int(_e) for _e in ele.split('__'))
      if id_project in map_project_users_ace :
        map_project_users_ace[id_project][id_user]=_acl_label
      else :
        map_project_users_ace[id_project] = {id_user:_acl_label}

    for id_project in map_project_users_ace :
      project = DBSession.query(Project).get(id_project)
      if project is not None:
        project.acls[0:] = []
        for id_user in map_project_users_ace[id_project] :
          _acl_label = map_project_users_ace[id_project][id_user]
          if _acl_label in Acl.known_acls:
             acl = Acl(id_user, id_project, _acl_label)
             DBSession.add(acl)
             project.acls.append(acl)
    DBSession.flush()
    result = True

  except IntegrityError as e:
    DBSession.rollback()
    result = False
    explanation = u"wtf ?"

  return HTTPFound(location=request.route_url(route_name='users'))
#------------------------------------------------------------------------------

@view_config(route_name='project_save_acls', renderer='json', permission='edit')
def save_project_acls(request):
  """
  """
  id_project = request.matchdict['id']
  project = DBSession.query(Project).get(id_project)

  result = False

  if project :
    try :
      # we remove old ACLs
      project.acls[0:] = []
      for ele, _acl_label in request.params.iteritems() :
        if ele.count('projectacl') and _acl_label in Acl.known_acls:

          # create acl object
          id_user = int(ele.split('_')[1])
          acl = Acl(id_user, id_project, _acl_label)

          # make the link with DBSession ...
          DBSession.add(acl)
          project.acls.append(acl)

      DBSession.flush()
      result = True
    except IntegrityError as e:
      log.error(e)
      DBSession.rollback()
      result = False
      explanation = u"wtf ?"

  return {'result':result}

#------------------------------------------------------------------------------

@view_config(route_name='project_fetch', renderer='json', permission='edit')
def fetch_project(request):
    """
    retrieve information about a project and send result in json
    this view is usable to compare projects
    """
    result = False
    id_project = request.matchdict['id']
    project = DBSession.query(Project).get(id_project)

    branch = None
    if 'branch' in request.params :
      branch = request.params['branch']

    limit = 200
    if 'limit' in request.params and request.params['limit'].isdigit():
      limit = int(request.params['limit'])

    repository_error = None

    try :
      with NodeController(project) as ssh_node :
        current_rev = ssh_node.get_current_rev_hash()
        last_hundred_change_list, map_change_sets = ssh_node.get_last_logs(limit, branch_filter=branch)
    except NodeException as e:
      repository_error = e.value
      log.error(e)
      last_hundred_change_list, map_change_sets = [], {}

    return { 'repository_error'         : repository_error,
             'last_hundred_change_list' : last_hundred_change_list}

#------------------------------------------------------------------------------

@view_config(route_name='project_revision_details', renderer='templates/revision.mako', permission='edit')
@view_config(route_name='project_revision_details_json', renderer='json', permission='edit')
def fetch_revision(request):
  """
  """
  id_project = request.matchdict['id']
  revision = request.matchdict['rev']

  project = DBSession.query(Project).get(id_project)

  diff = ""
  revision_description = {}

  with NodeController(project, silent=True) as ssh_node :
    diff = ssh_node.get_revision_diff(revision)
    revision_description = ssh_node.get_revision_description(revision)

  return {'diff'     : diff,
          'project'  : project,
          'revision' : revision_description}

#------------------------------------------------------------------------------

@view_config(route_name='project_change_to', permission='edit', renderer='json')
def update_project_to(request):
  """
  """
  id_project = request.matchdict['id']

  brothers_id_project = list(request.matchdict['brother_id'])
  brothers_id_project.append(id_project)

  revision = request.matchdict['rev']
  projects_to_update = [DBSession.query(Project).options(joinedload(Project.tasks)).get(_id_project) for _id_project in brothers_id_project]

  thread_stack       = []

  for __p in projects_to_update:
    new_thread = SpeedUpdater(__p, revision)
    thread_stack.append(new_thread)
    new_thread.start()

  t0 = time.time()
  while sum([e.is_stopped() for e in thread_stack])!=len(projects_to_update) or time.time()>(t0+10*60):
    time.sleep(0.005)

  # harvest additional tasks exceptions
  task_abnormal = {}
  for thread in thread_stack :
    side_exceptions = thread.get_tasks_exceptions()
    if len(side_exceptions)>0 :
      task_abnormal[thread.project.id] = []
    for task_exception_value in side_exceptions :
      task_abnormal[thread.project.id].append(task_exception_value)

  result = {t.project.id:t.project_updated() for t in thread_stack}
  return {'result':result, 'task_abnormal':task_abnormal}

#------------------------------------------------------------------------------

