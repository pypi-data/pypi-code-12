#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under the
# terms of the M.I.T License.
#

import paramiko
import time
import logging
import socket
import threading
import re
import os.path
import logging
import uuid
import sys

from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles

styles = list(get_all_styles())

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------

if sys.version < '3':
    def u(x, codec):
        return x.decode(codec)
else:
    def u(x, codec):
        return str(x, codec)

#------------------------------------------------------------------------------

class NodeException(Exception):
  """
  """

  def __init__(self, value):
      self.value = value

#------------------------------------------------------------------------------

class HgNewBranchForbidden(Exception):
  """
  """

  def __init__(self, value):
      self.value = value

#------------------------------------------------------------------------------

class HgNewHeadsForbidden(Exception):
  """
  """

  def __init__(self, value):
      self.value = value

#------------------------------------------------------------------------------

class OutputErrorCode(Exception):
  """
  """

  def __init__(self, value):
      self.value = value

#------------------------------------------------------------------------------

class OutputError(Exception):
  """
  """

  def __init__(self, value):
      self.value = value

#------------------------------------------------------------------------------

def check_connections(function):
  """
    A decorator to check SSH connections.
  """

  def deco(self, *args, **kwargs):
      if self.ssh is None:
          self.ssh = self.get_ssh()
      else:
          ret = getattr(self.ssh.get_transport(), 'is_active', None)
          if ret is None or (ret is not None and not ret()):
              self.ssh = self.get_ssh()
      return function(self, *args, **kwargs)
  return deco

#------------------------------------------------------------------------------

class DiffWrapper(object):
  """
  """

  def __init__(self, raw_diff):
    """
    """
    self.raw_diff = raw_diff

    self.lst_files = []
    self.dict_files = []
    self.lst_basename_files = []

    if self.raw_diff :
      # we init content ...
      self.lst_files = self.__get_lst_files()
      self.lst_basename_files = [os.path.basename(f_name) for f_name in self.lst_files]
      self.dict_files = self.__get_files_to_diff()

  def __get_lst_files(self):
    """
    """
    # add some non capturing group for revision argument ... (just for remind !)
    groups = re.findall(u"diff(?: -r [a-z0-9]+){1,2} (?P<file_name>.+)$",self.raw_diff, re.MULTILINE)
    return groups

  def __get_files_to_diff(self):
    """
    """
    groups = self.__get_lst_files()
    diffs_content = [highlight(bloc, DiffLexer(), HtmlFormatter(cssclass=u'source', style=u'colorful')) for bloc in re.split(u"\n*diff -r [a-z0-9]{8,20} [^\n]+\n",self.raw_diff) if bloc.strip()]
    return dict(zip(groups, diffs_content))

  def __json__(self, request):
    """
    """
    return { u'id':self.raw_diff,
             u'lst_files':self.lst_files,
             u'lst_basename_files':self.lst_basename_files,
             u'dict_files':self.dict_files
           }


#------------------------------------------------------------------------------

class NodeSsh(object):
  """
  """

  logs = []
  max_timeout = 60*5
  
  def __init__(self, uri, project_id):
    """
      uri should like this

      "{user}:{password}@{host}:{path}"

    :param uri: an string that looks like "{user}:{password}@{host}:{path}"
    """
    self.uri = uri
    self.project_id = project_id
    user,password_host,path = uri.split(u':')

    self.user = user
    self.path = path
    self.password, self.host = password_host.split(u'@')

    self.ssh = self.get_ssh()
    self.lock = threading.Lock()
    self.last_release_lock_event = None

    self.__state_locked = False


  def add_to_log(self, command) :
    """
    """
    self.__class__.logs.append((self.project_id, self.host, self.path, re.sub(u"^cd[^;]*;",'',command)))

  def lock_it(self):
    """
    """
    # we release it ...
    with self.lock :
      self.__state_locked = True

  def is_locked(self):
    """
    """
    return self.__state_locked

  def release_lock(self):
    """
    """
    # we release it ...
    with self.lock :
      self.__state_locked = False
      self.last_release_lock_event = time.time()

  def decode_raw_bytes(self, bytes_content):
    """
    :param bytes_content: octet string an 2.x 3x bytes string decode wrapper
    """
    content = ""
    for codec in (u'utf-8', u'latin-1') :
      try :
        content = u(bytes_content, codec)
      except Exception as e:
        content = ""
      else :
        break
    return content

  def get_ssh(self):
    """
      get the ssh object connection.
    """
    try :
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(self.host, username=self.user, password=self.password)
    except socket.gaierror :
      raise NodeException(u"host unavailable")
    except paramiko.ssh_exception.AuthenticationException :
      raise NodeException(u"wrong password or user is not allowed to connect to host")
    except paramiko.ssh_exception.BadAuthenticationType :
      raise NodeException(u"wrong password or user is not allowed to connect to host")
    except paramiko.ssh_exception.BadHostKeyException :
      raise NodeException(u"The host key given by the SSH server did not match what we were expecting.")
    except paramiko.ssh_exception.PasswordRequiredException :
      raise NodeException(u"Exception raised when a password is needed to unlock a private key file.")
    except TypeError :
      raise NodeException(u"host unavailable")
    return ssh

  def close_connection(self):
    """
    """
    with self.lock :
      self.ssh.close()
      self.last_release_lock_event = None
      log.info("this connection hasn't been used from long time ago, closing connection to : %s"%self.host)

  @check_connections
  def run_command_and_feed_password_prompt(self, command, password, reg_password ='password: ', reg_shell = '[^\n\r]+@[^\n\r]+\$', log_it=True):
    '''
      Execute command through SSH and also feed prompt !

      we may return the full dialog text content.
      so upper layer could test some things like

      --new-branch not allowed on push and so on ...

    '''
    guid = uuid.uuid1().hex
    global_buff_content = ""

    # add a foot print as a guid
    # so we are sure
    command += u";echo '%s'"%guid

    full_log = []

    channel = self.ssh.invoke_shell()
    channel.settimeout(self.__class__.max_timeout)

    # We received a potential prompt.
    # something like toto@hostname:~$
    buff = ''
    t0 = time.time()
    time_out = False
    full_log.append(u'org_command %s'%command)

    wait_time = 0.05
    while len(re.findall(reg_shell, buff, re.MULTILINE))==0:
        resp = channel.recv(9999)
        buff += self.decode_raw_bytes(resp)
        global_buff_content += "\n" + buff

        time.sleep(wait_time)
        wait_time += 0.05

        if time.time() - t0 > 60 :
          time_out = True
          break
    full_log.append(u'buff1 %s'%buff)

    if not time_out :
      # ssh and wait for the password prompt.
      channel.send(command + '\n')

      buff = ''
      t0 = time.time()
      wait_time = 0.05
      while not buff.endswith(reg_password):
          resp = channel.recv(9999)
          buff += self.decode_raw_bytes(resp)
          global_buff_content += "\n" + buff

          time.sleep(wait_time)
          wait_time += 0.05

          if time.time()-t0 > 60 :
            time_out = True
            break
      full_log.append(u'buff2 %s'%buff)

    if not time_out :
      # Send the password and wait for a prompt.
      channel.send(password + '\n')
 
      buff = u''
      t0 = time.time()
      # wait : 'added 99 changesets with 243 changes to 27 files'
      # wait : "(run 'hg update' to get a working copy)"
      #
      # sample pushing ...
      #
      # searching for changes
      # remote: adding changesets
      # remote: adding manifests
      # remote: adding file changes
      # remote: added 90 changesets with 102 changes to 68 files
      wait_time = 0.05
      while buff.find(u'to get a working copy') < 0 and buff.find(u'changesets with') < 0 and buff.find(u"abort: push creates new remote branches") < 0 and len(re.findall(reg_shell, buff, re.MULTILINE))==0 and buff.find(guid)<0:
          resp = channel.recv(9999)
          buff += self.decode_raw_bytes(resp)
          global_buff_content += "\n" + buff

          time.sleep(wait_time)
          wait_time += 0.05
          if time.time() - t0 > 60 :
            time_out = True
            break

      full_log.append(u'buff2 %s'%buff)
      ret=buff

    if channel :
      channel.close()

    self.release_lock()

    if log_it :
      self.add_to_log(command)

    exit_status = channel.recv_exit_status()

    return {u'out'         : full_log,
            u'err'         : [],
            u'retval'      : [],
            u'exit_status' : exit_status,
            u'buff'        : global_buff_content}

  @check_connections
  def run_command(self, command, log=False):
    ''' Executes command through SSH tunnel. '''
    # we lock threads per resource
    with self.lock :
      try :
        stdin, stdout, stderr = self.ssh.exec_command(command)
        stdin.flush()
        stdin.channel.shutdown_write()

        exit_status = stdin.channel.recv_exit_status()
        ret         = stdout.read()
        err         = stderr.read()

        if err:
          raise NodeException(self.decode_raw_bytes(err))
        elif exit_status != 0 :
          raise OutputErrorCode(exit_status)
        elif ret:
          if log :
            self.add_to_log(command)

          if(type(ret)==bytes):
            ret = self.decode_raw_bytes(ret)
          return ret
        else:
          return None
      except socket.gaierror :
        raise NodeException(u"host unavailable")

      self.release_lock()

  def compare_release_a_sup_equal_b(self, release_a, release_b):
    """
    """
    tab_a = [int(e) for e in release_a.split(u'.')]
    tab_b = [int(e) for e in release_b.split(u'.')]

    result = False

    for i in range(len(tab_a)) :
      ele_a = tab_a[i]

      if len(tab_b) >= i+1 :
        ele_b = tab_b[i]
      else :
        ele_b = 0

      if (ele_a > ele_b) :
        result = True
        break
      elif (ele_a < ele_b) :
        result = False
        break

    return result

#------------------------------------------------------------------------------

class HgNode(NodeSsh):
  """
    Some node to manipulate remote hg repository
  """

  _template = u"{node}|#|{p1node}|#|{p2node}|#|{author}|#|{branches}|#|{rev}|#|{parents}|#|{date|isodate}|#|{desc|json}|#|{tags}\n" 

  def get_content(self, revision, file_name):
    """
    """
    try :
      data = self.run_command(u"cd %s ; hg cat -r %s %s"%(self.path, revision, file_name))
    except Exception as e:
      data = None
    return data


  def get_release(self):
    """
    """
    try :
      data = self.run_command(u"cd %s ; hg --version"%self.path)
      data = re.findall(u'\((?:version) (?P<version>[0-9\.]+)\)',data)
      if data : 
        data = data[0]
      else :
        data = None
    except Exception as e:
      data = None
    return data

  def get_current_rev_hash(self):
    """
    """
    try :
      data = self.run_command(u"cd %s ; hg --debug id -i"%self.path)
    except NodeException as e :
      result = None
    else :
      # hg may add '+' to indicate tip release
      # '+' is not part of changeset hash
      result = data.strip(u'\n').split(u' ')[0].strip(u'+')
    return result

  def pullable(self, local_project, target_project):
    """
    try to check if between two input projects we can push

    :param local_project: an alchemy Project object 
    :param target_project: an alchemy Project object
    """
    if not local_project.dvcs_release :
      local_project.dvcs_release = self.get_release()

    if (local_project.dvcs_release is not None and self.compare_release_a_sup_equal_b(local_project.dvcs_release, '1.7.4')) :
      insecure = u" --insecure "
    else:
      # what ever mercurial release, even if its not mandatory
      # we feed that param
      insecure = u" --insecure "
    data = self.run_command_and_feed_password_prompt(u'cd %s ; hg in -l 1 %sssh://%s@%s/%s'%(
                                                        self.path,
                                                        insecure,
                                                        target_project.user,
                                                        target_project.host,
                                                        target_project.path),
                                                        target_project.password,
                                                        log_it=False)
    return data['buff'].count('changeset:')>0

  def pushable(self, local_project, target_project):
    """
    try to check if between two input projects we can push

    :param target_project: an SshNode
    """
    if not local_project.dvcs_release :
      local_project.dvcs_release = self.get_release()

    if (local_project.dvcs_release is not None and self.compare_release_a_sup_equal_b(local_project.dvcs_release, '1.7.4')) :
      insecure = u" --insecure "
    else:
      # what ever mercurial release, even if its not mandatory
      # we feed that param
      insecure = u" --insecure "
    data = self.run_command_and_feed_password_prompt(u'cd %s ; hg out -l 1 %sssh://%s@%s/%s'%(
                                                        self.path,
                                                        insecure,
                                                        target_project.user,
                                                        target_project.host,
                                                        target_project.path),
                                                        target_project.password,
                                                        log_it=False)
    return data['buff'].count('changeset:')>0

  def push_to(self, local_project, target_project, force_branch):
    """
    this may method may raise an exception

    :param target_project: an alchemy Project object
    :param force_branch: and boolean to force push 
    """
    if force_branch :
      new_branch_arg = ' --new-branch'
    else : 
      new_branch_arg = ''

    if not local_project.dvcs_release :
      local_project.dvcs_release = self.get_release()

    if (local_project.dvcs_release is not None and self.compare_release_a_sup_equal_b(local_project.dvcs_release, '1.7.4')) :
      insecure = u" --insecure "
    else:
      # what ever mercurial release, even if its not mandatory
      # we feed that param
      insecure = u" --insecure "

    data = self.run_command_and_feed_password_prompt(u'cd %s ; hg push%sssh://%s@%s/%s%s'%(
                                                        self.path,
                                                        insecure,
                                                        target_project.user,
                                                        target_project.host,
                                                        target_project.path,
                                                        new_branch_arg),
                                                        target_project.password)
    if not force_branch and ( data['buff'].count('--new-branch') or data['buff'].count('creates new remote branches')):
      raise HgNewBranchForbidden(data)
    elif not force_branch and data['buff'].count('details about pushing new heads') :
      raise HgNewHeadsForbidden(data)
    elif data['buff'].count('remote: abort:') :
      # might be related to unknown node
      raise OutputError(data)
    elif data['exit_status']==255:
      # regarding to documentation hg
      # have a look to `hg st &> /dev/null  ; echo $?`
      raise OutputErrorCode(data)
    return data

  def pull_from(self, local_project, source_project):
    """
    :param source_project: an alchemy Project object
    """
    if not local_project.dvcs_release :
      local_project.dvcs_release = self.get_release()

    if (local_project.dvcs_release is not None and self.compare_release_a_sup_equal_b(local_project.dvcs_release, '1.7.4')) :
      insecure = " --insecure "
    else:
      # what ever mercurial release, even if its not mandatory
      # we feed that param
      insecure = u" --insecure "

    data = self.run_command_and_feed_password_prompt(u'cd %s ; hg pull%sssh://%s@%s/%s'%(self.path,
                                                            insecure,
                                                            source_project.user,
                                                            source_project.host,
                                                            source_project.path),
                                                            source_project.password)

  def get_last_logs_starting_from(self, start_from_this_hash_revision) :
    """
      return last logs ... because we use hash start mercurial will reverse list output

      :param start_from_this_hash_revision: hash string, the revision hash from which we retrieve log 
    """
    data = self.run_command(u'cd %s ; hg log --template "%s" -r%s:'%(self.path, self._template, start_from_this_hash_revision))
    list_nodes = []
    map_nodes = {}

    if data :
      data = (line for line in data.splitlines())
      for line in reversed(tuple(data)) :
        node, p1node, p2node, author, branch, rev, parents, date, desc, tags = line.split(u'|#|')
        desc = desc.replace(u'\\n','\n').strip('"')
        if not branch : branch = 'default'
        if len(p2node.strip('0'))==0 :
          p2node = None
        list_nodes.append({'node':node, 'p1node':p1node, 'p2node':p2node, 'branch':branch, 'author':author, 'rev':rev, 'parents':parents, 'desc':desc, 'tags':tags, 'date':date})
        map_nodes[node]=list_nodes[-1]
    return list_nodes, map_nodes

  def get_last_logs(self, nb_lines, branch_filter=None, revision_filter=None):
    """
      return last logs ...

      :param nb_lines: integer, limit the number of lines
      :param branch_filter: an branch name (string) that can filter result
      :param revision_filter: an revision hash (string) that can filter result
    """

    if revision_filter :
      data = self.run_command(u'cd %s ; hg log --template "%s" -r %s'%(self.path, self._template, revision_filter))
    elif branch_filter :
      data = self.run_command(u'cd %s ; hg log -l %d --template "%s" -b %s'%(self.path, nb_lines, self._template, branch_filter))
    else :
      data = self.run_command(u'cd %s ; hg log -l %d --template "%s"'%(self.path, nb_lines, self._template))

    list_nodes = []
    map_nodes = {}

    if data :
      data = (line for line in data.splitlines())

      for line in data :
        node, p1node, p2node, author, branch, rev, parents, date, desc, tags = line.split(u'|#|')
        desc = desc.replace(u'\\n','\n').strip('"')
        if not branch : branch = 'default'
        if len(p2node.strip('0'))==0 :
          p2node = None
        list_nodes.append({'node':node, 'p1node':p1node, 'p2node':p2node, 'branch':branch, 'author':author, 'rev':rev, 'parents':parents, 'desc':desc, 'tags':tags, 'date':date})
        map_nodes[node]=list_nodes[-1]

    return list_nodes, map_nodes

  def get_file_content(self, file_name, revision):
    """
    :param file_name: the file name (string)
    :param revision: the revision hash (string)
    """
    try :
      result = self.run_command(u"cd %s ; hg cat %s -r %s"%(self.path, file_name, revision))
    except NodeException as e :
      result = None
    return result
    
  def get_initial_hash(self):
    """
      return the initial hash (revision 0)
      :return: string hash
    """
    try :
      data = self.run_command(u"cd %s ; hg --debug id -i -r 0"%self.path)
    except NodeException as e :
      result = None
    else :
      # hg may add '+' to indicate tip release
      # '+' is not part of changeset hash
      result = data.strip(u'\n').split(u' ')[0].strip(u'+')
      if not result or len(result)<35:
        result = None
    return result
     
  def get_tags(self):
    """
      return a list of tags labels
    """
    tags_and_key_revisions = []
    try :
      data = self.run_command(u'cd %s ; hg tags'%(self.path))
    except NodeException as e :
      pass
    else :
      tags_and_key_revisions = sorted((re.sub(' {2,}',' ',e).split(u' ') for e in data.strip().split(u'\n') if e.split(u' ')[0]))
    
    return tags_and_key_revisions

  def get_branches(self):
    """
      return a list of branches labels
    """
    branches = []
    try :
      data = self.run_command(u'cd %s ; hg branches'%(self.path))
    except NodeException as e :
      pass
    else :
      if data :
        branches = sorted((e.split(u' ')[0] for e in data.strip().split(u'\n') if e.split(u' ')[0]))

    return branches

  def get_current_revision_description(self):
    """
    """
    node = {}
    try :
      data = self.run_command(u'''cd %s ; hg --debug id | cut -d' ' -f 1 | tr -d ' +' | xargs -I {} hg log -r {} --template "%s"'''%(self.path, self._template))
    except NodeException as e :
      node = {}
    else :
      node, p1node, p2node, author, branch, rev, parents, date, desc, tags = data.split(u'|#|')
      desc = desc.replace(u'\\n','\n').strip('"')
      if not branch : branch = 'default'
      if len(p2node.strip('0'))==0 :
        p2node = None
      node = {'node':node, 'p1node':p1node, 'p2node':p2node, 'branch':branch, 'author':author, 'rev':rev, 'parents':parents, 'desc':desc, 'tags':tags, 'date':date}
    return node 

  def get_revision_diff(self, revision):
    """
    :param revision: the revision hash (string)
    """
    diff_content = ""
    try :
      diff_content = self.run_command(u'''cd %s ; hg diff -c %s'''%(self.path, revision))
    except NodeException as e :
      diff_content = "" 
    return DiffWrapper(diff_content)

  def get_revision_description(self, revision):
    """
    :param revision: the revision hash (string)
    """
    list_nodes, map_nodes = self.get_last_logs(1, revision_filter=revision)
    first_node = {}
    if list_nodes :
      first_node = list_nodes[0]
    return first_node

  def update_to(self, revision):
    """
    update project to a certain release
    :param revision: string, the revision hash
    """
    result = True
    try :
      data = self.run_command(u'cd %s ; hg update -C -r %s'%(self.path, revision), True)
    except NodeException as e :
      result = False
    return result

#------------------------------------------------------------------------------

class GitNode(NodeSsh):
  """
    A specific node to manipulate remote git repository 
  """

  _template = u"%H|#|%cn|#|{branches}|#|{rev}|#|%P|#|{date}|#|{desc|jsonescape}|#|{tags}\n"

  def get_release(self):
    """
    """
    try :
      data = self.run_command(u"cd %s ; git --version --no-color"%self.path)
      data = re.findall(u'(?:version) (?P<version>[0-9\.]+)', data)
      if data : 
        data = data[0]
      else :
        data = None
    except Exception as e:    
      data = None             
    return data

  def get_current_rev_hash(self):
    """
      commit 1ea7f6aa3feef3e257e3fe4fde6b6994983c6062
      Author: sbard <toto.free.fr>
      Date:   Wed Sep 10 10:10:27 2014 +0200
      
          fix test
      
      diff --git a/toto.txt b/toto.txt
      new file mode 100644
      index 0000000..e69de29
    """
    try :
      data = self.run_command(u"cd %s ; git rev-parse HEAD --no-color"%self.path)
    except NodeException as e :
      result = None
    else :
      result = data.strip(' \n')
    return result

  def push_to(self, local_project, target_project, force_branch):
    """
    """
    data = self.run_command_and_feed_password_prompt(u'cd %s ; git push%sssh://%s@%s/%s'%(
                                                        self.path,
                                                        target_project.user,
                                                        target_project.host,
                                                        target_project.path),
                                                        target_project.password)

  def pull_from(self, local_project, source_project):
    """
    """
    data = self.run_command_and_feed_password_prompt(u'cd %s ; git pull%sssh://%s@%s/%s'%(self.path,
                                                            source_project.user,
                                                            source_project.host,
                                                            source_project.path),
                                                            source_project.password)

  def get_last_logs(self, nb_lines, branch_filter=None, revision_filter=None):
    """
      return last logs ...
      :param nb_lines: integer, limit the number of lines
    """
    try :
      if revision_filter :
        data = self.run_command(u'cd %s ; git --no-pager log --pretty=format:%s -r %s'%(self.path, self._template, revision_filter))
      elif branch_filter :
        data = self.run_command(u'cd %s ; git --no-pager log -n %d --pretty=format:%s HEAD %s'%(self.path, nb_lines, self._template, branch_filter))
      else :
        data = self.run_command(u'cd %s ; git --no-pager log -n %d --pretty=format:%s'%(self.path, nb_lines, self._template))
    except NodeException as e :
      data = ""

    list_nodes = []
    map_nodes = {}

    if data :
      data = (line for line in data.splitlines())
      for line in data :
        node, author, branch, rev, parents, desc, tags = line.split(u'|#|')
        desc = desc.replace(u'\\n','\n').strip('"')
        if not branch : branch = 'default'
        list_nodes.append({'node':node, 'branch':branch, 'author':author, 'rev':rev, 'parents':parents, 'desc':desc, 'tags':tags, 'date':date})
        map_nodes[node]=list_nodes[-1]

    return list_nodes, map_nodes

  def get_file_content(self, file_name, revision):
    """
    """
    try :
      result = self.run_command(u"cd %s ; git cat %s -r %s"%(self.path, file_name, revision))
    except NodeException as e :
      result = None
    return result

  def get_initial_hash(self):
    """
      return the initial hash (revision 0)
      :return: string hash
    """
    try :
      data = self.run_command(u"cd %s ; git rev-list --max-parents=0 HEAD --no-color"%self.path)
    except NodeException as e :
      result = None
    else :
      result = data.strip(u' \n')
    return result

  def get_branches(self):
    """
      return a list of branches labels
    """
    branches = []
    try :
      data = self.run_command(u"cd %s ; git for-each-ref --count=30 --sort=-committerdate refs/heads/ --format='%(refname:short)'"%(self.path))
    except NodeException as e :
      pass
    else :
      branches = sorted((e.strip() for e in data.strip().split(u'\n') if e.strip()))
    return branches

  def get_current_revision_description(self):
    """
    """
    node = {}
    try :
      data = self.run_command(u'''cd %s ; git --debug id | cut -d' ' -f 1 | tr -d ' +' | xargs -I {} hg log -r {} --template "%s"'''%(self.path, self._template))
    except NodeException as e :
      node = {}
    else :
      node, author, branch, rev, parents, date, desc, tags = data.split(u'|#|')
      desc = desc.replace(u'\\n','\n').strip('"')
      if not branch : branch = 'default'
      node = {'node':node, 'branch':branch, 'author':author, 'rev':rev, 'parents':parents, 'desc':desc, 'tags':tags, 'date':date}
    return node 

  def get_revision_diff(self, revision):
    """
    :param revision: the revision hash
    """
    diff_content = ""
    try :
      diff_content = self.run_command(u'''cd %s ; git diff -c %s'''%(self.path, revision))
    except NodeException as e :
      diff_content = "" 
    return DiffWrapper(diff_content)

  def get_revision_description(self, rev):
    """
    """
    list_nodes, map_nodes = self.get_last_logs(1, revision_filter=rev)
    first_node = {}
    if list_nodes :
      first_node = list_nodes[0]
    return first_node

  def update_to(self, rev):
    """
    update project to a certain release
    :param rev: string, the revision hash
    """
    result = True
    try :
      data = self.run_command(u'cd %s ; git reset ; git reset %s'%(self.path, rev), True)
    except NodeException as e :
      result = False
    return result

#------------------------------------------------------------------------------

class NodeController(object):
  """
     control an ssh node and release the lock
     when we finish to use it

     this implement a with statement 

     sample usage ::

      with NodeController(project, silent=True) as ssh_node :
        result = ssh_node.pushable(project, target_project)

     silent key-param could be provided to control that 'with' statement
     will re-raise exception
  """

  def __init__(self, project, silent=False):
    """
    :param Project project: an alchemy model
    :key-param silent: don't re-raise exception if something happen
                       the node will just release the lock and log
                       the error
    """
    self.project = project
    self.silent = silent

  def __enter__(self):
    """
    """
    self.ssh_node = self.project.get_ssh_node()
    return self.ssh_node

  def __exit__(self, exc_type, exc_value, traceback):
    """
    python will re-raise error regarding to exit output
    """
    result = False

    if exc_value :
      log.error(exc_value)

      if(self.silent) :
        result = True
      else :
        result = False
    else :
      result = False

    if self.ssh_node :
      self.ssh_node.release_lock()

    return result
   
#------------------------------------------------------------------------------

class PoolSsh(object):
  """
  pool of ssh connection to maintain, recycle
  check and so on ...
  """

  nodes = {}
  max_nodes_in_pool = 4
  # seconds ...
  time_elapse_before_closing_connection = 3600

  @classmethod
  def close_un_used_nodes(cls):
    """
    we close nodes that are unused ...
    """
    for key_uri in cls.nodes :
      for _node in cls.nodes[key_uri] :
        if not _node.is_locked() and _node.last_release_lock_event is not None :
          if time.time() - _node.last_release_lock_event > cls.time_elapse_before_closing_connection :
            # lets close the connection
            # and put it in None state
            _node.close_connection()

  @classmethod
  def delete_nodes(cls, uri):
    """
    when a project is deleted we should also remove HgNode object
    to avoid confusion ...
    """
    if uri in cls.nodes :
      del cls.nodes[uri][0:]

  @classmethod
  def log_nodes_state(cls):
    """
    """
    for key_uri in cls.nodes :
      for _node in cls.nodes[key_uri] :
        log.info("STATE is locked ?: %s" % _node.is_locked())

  @classmethod
  def get_key_hash_node(cls, uri):
    """
    """
    # uri is a too large key for gathering connection
    # we should use a more accurate one
    # lets try user+host
    user,password_host,path = uri.split(u':')
    password, host = password_host.split(u'@')
    return user+host

  @classmethod
  def get_node(cls, uri, project_id):
    """
    try to acquire a free ssh channel or open a new one ...

    :param uri: the ssh url for the project
    :param project_id: an integer (the project.id)
    """
    node = None
    key_uri_node = uri 

    if key_uri_node not in cls.nodes :
      cls.nodes[key_uri_node] = [HgNode(uri, project_id)]
      node = cls.nodes[key_uri_node][0]
    else :
      t0 = time.time()

      # we wait 60 seconds
      # we wait to acquire a node (wait for a free node)
      while node is None and  time.time() - t0 < 60 :

        if time.time() - t0 > 1 :
          time.sleep(1)

        for __node in cls.nodes[key_uri_node] :
          if not __node.is_locked() :
            __node.lock_it()
            node = __node
            break

        if node is None and len(cls.nodes[key_uri_node]) < cls.max_nodes_in_pool :
          log.warning(u"creating additional node in pool (%s)"%(len(cls.nodes[key_uri_node])))
          node = HgNode(uri, project_id)
          # this one is unknown of the other threads ...
          # we lock it immediatly
          node.lock_it()
          cls.nodes[key_uri_node].append(node)

    return node

