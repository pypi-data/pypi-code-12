#!/usr/bin/python
import os
import ast
import json
import yaml
import jinja2
import argparse
import commands


## Exceptions
class FileNotFound(Exception):
  pass
class CommandFailed(Exception):
  pass


class Utils:
  def update_tree(self,data,function,namespace=None):
    try: assert not data == None
    except: raise Exception('Utils.update_tree.data cannot be None')
    try: assert not function == None
    except: raise Exception('Utils.update_tree.function cannot be None')
    if namespace == None:
      namespace = data
    if type(data) == type({}):
      for n in data:
        data[n] = self.update_tree(data[n],function,namespace)
    elif type(data) == type([]):
      c = 0
      for i in data:
        data[c] = self.update_tree(i,function,namespace)
        c += 1
    else:
      data = function(data,namespace)
    return(data)

## Params
class Parameters:

  filepaths      = None
  debug          = None
  ignore_cmd_err = None
  params         = None


  def __init__(self,filepaths,ignore_cmd_err=False,debug=False):
    try: assert not filepaths == None
    except: raise Exception('Parameters.__init__.filepaths cannot be None')
    try: assert not ignore_cmd_err == None
    except: raise Exception('Parameters.__init__.ignore_cmd_err cannot be None')
    try: assert not debug == None
    except: raise Exception('Parameters.__init__.debug cannot be None')
    self.filepaths = filepaths
    self.debug = debug
    self.ignore_cmd_err = ignore_cmd_err
    self.utils = Utils()
    self.load(self.filepaths)


  def load(self,filepaths):
    try: assert not filepaths == None
    except: raise Exception('Parameters.load.filepaths cannot be None')
    self.params = {}
    for i in filepaths:
      try:
        assert os.path.isfile(i)
      except Exception as e:
        raise FileNotFound('Cannot find file {}'.format(i))
        print(e)
      with open(i,'r') as f:
        param_text = f.read()
      try:
        p = yaml.load(param_text)
        self.params = dict(self.params, **p)
      except:
        p = json.loads(param_text)
        self.params = dict(self.params, **p)


  def resolve_tree(self,data,namespace):
    try: assert not data == None
    except: raise Exception('Parameters.resolve_tree.data cannot be None')
    try: assert not namespace == None
    except: raise Exception('Parameters.resolve_tree.namespace cannot be None')
    data = str(data)
    data = jinja2.Environment().from_string(data).render(namespace)
    try:
      data = ast.literal_eval(data)
    except:
      pass
    if type(data) == type(u''):
      if data.startswith('<[') and data.endswith(']>'):
        cmd = data.lstrip('<[').rstrip(']>')
        status = commands.getstatusoutput(cmd)
        if not self.ignore_cmd_err:
          try:
            assert status[0] == 0
          except:
            raise CommandFailed('Command "{}" exited with a nonzero value!'.format(cmd))
        data = status[-1]
    return(data)


  def resolveYAMLJinja(self,data,evals=25):
    try: assert not data == None
    except: raise Exception('Parameters.resolveYAMLJinja.data cannot be None')
    try: assert not evals == None
    except: raise Exception('Parameters.resolveYAMLJinja.evals cannot be None')
    for i in range(0,evals):
      data = self.utils.update_tree(data,self.resolve_tree)
    return(data)



## Template
class Template:
  template_text  = None
  ignore_cmd_err = None
  debug = None


  def __init__(self,filepath,ignore_cmd_err=False,debug=False):
    assert not filepath == None
    assert not ignore_cmd_err == None
    assert not debug == None
    self.ignore_cmd_err = ignore_cmd_err
    self.debug          = debug
    self.load(filepath)
    self.utils = Utils()


  def load(self,filepath):
    assert not filepath == None
    try:
      assert os.path.isfile(filepath)
    except Exception as e:
      raise FileNotFound('Cannot find file {}'.format(filepath))
      print(e)
    with open(filepath,'r') as f:
      self.template_text = f.read()


  def render_jinja(self,data,namespace):
    try: assert not data == None
    except: raise Exception('Template.data cannot be None')
    try: assert not namespace == None
    except: raise Exception('Template.namespace cannot be None')
    data = str(data)
    data = jinja2.Environment().from_string(data).render(namespace)
    try:
      data = ast.literal_eval(data)
    except:
      pass
    if type(data) == type(u''):
      if data.startswith('<[') and data.endswith(']>'):
        cmd = data.lstrip('<[').rstrip(']>')
        status = commands.getstatusoutput(cmd)
        if not self.ignore_cmd_err:
          try:
            assert status[0] == 0
          except:
            raise CommandFailed('Command "{}" exited with a nonzero value!'.format(cmd))
        data = status[-1]
    return(data)


  def resolveYAMLJinja(self,data,evals=25):
    try: assert not data == None
    except: raise Exception('Template.resolveYAMLJinja.data cannot be None')
    for i in range(0,evals):
      data = self.utils.update_tree(data,self.render_jinja)
    return(data)


  def render(self,params):
    try: assert not params == None
    except: raise Exception('Template.render.params cannot be None')
    params = self.resolveYAMLJinja(params)
    render = jinja2.Environment().from_string(self.template_text).render(params)
    if self.debug:
      return('{}'.format(json.dumps(params,indent=2)))
    else:
      return(render)




## Shell
class Shell:
  results = None
  def __init__(self):
    parser = argparse.ArgumentParser(description='Generic file template generator')
    parser.add_argument('--template', '-t',             action="store",      dest="template_path",  default=False, help='Path to template file',                required = True)
    parser.add_argument('--parameters', '-p',           action="store",      dest="param_paths",    default=False, help='Path to parameter file(s)', nargs='*', required = True)
    parser.add_argument('--debug', '-d',                action="store_true", dest="debug",          default=False, help='Show the params')
    parser.add_argument('--ignore-command-error', '-i', action="store_true", dest="ignore_cmd_err", default=False, help='Allows the tool to ignore nonzero exit codes on <[metacommands]>')
    parser.add_argument('--version', action='version',  version='%(prog)s 1.0')
    self.results = parser.parse_args()
    template     = Template(filepath=self.results.template_path,ignore_cmd_err=self.results.ignore_cmd_err)
    params       = Parameters(filepaths=self.results.param_paths,ignore_cmd_err=self.results.ignore_cmd_err)
    print(template.render(params=params.params))


def shell_start():
  shell = Shell()


