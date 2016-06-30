##############################################################################
#
# Copyright (c) 2010 ViFiB SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os
import zc.buildout
import sys
import logging
import subprocess

def extension(buildout):
  Rebootstrap(buildout)()

class Rebootstrap:
  def __init__(self, buildout):
    self.logger = logging.getLogger(__name__)
    self.buildout = buildout
    buildout_directory = buildout['buildout']['directory']
    self.rebootstrap_directory = os.path.join(
      buildout_directory, 'rebootstrap'
    )
    # fetch section to build python, obligatory
    self.python_section = (
      buildout['buildout'].get('python') or \
      buildout['rebootstrap']['section']
    ).strip()
    self.wanted_python = buildout[self.python_section]['executable'].replace(
      buildout_directory, self.rebootstrap_directory
    )
    # query for currently running python
    self.running_python = sys.executable

  def __call__(self):
    if self.running_python != self.wanted_python:
      self.install_section()
      self.reboot()

  def reboot(self):
    message = """
************ REBOOTSTRAP: IMPORTANT NOTICE ************
bin/buildout is being reinstalled right now, as new python:
  %(wanted_python)s
is available, and buildout is using another python:
  %(running_python)s
Buildout will be restarted automatically to have this change applied.
************ REBOOTSTRAP: IMPORTANT NOTICE ************
""" % dict(wanted_python=self.wanted_python,
    running_python=self.running_python)
    self.logger.info(message)
    args = map(zc.buildout.easy_install._safe_arg, sys.argv)
    env = os.environ
    os.execve(self.wanted_python, [self.wanted_python] + args, env)

  def install_section(self):
    # For safety, we always try to install/update instead of the condition
    # if not os.path.exists(self.wanted_python):
    if True:
      self.logger.info('Installing section %r to provide %r' % (
        self.python_section, self.wanted_python))
      args = map(zc.buildout.easy_install._safe_arg, sys.argv)
      if 'install' in args:
        args =  args[:args.index('install')]

      # explicitly specify the config file location by absolute path
      if '-c' not in args:
        config_file = os.path.abspath(os.path.join(
          os.curdir, 'buildout.cfg'))
        args.extend(['-c', config_file])
      else:
        config_file = args[args.index('-c') + 1]
        if not zc.buildout.buildout._isurl(config_file):
          config_file = os.path.abspath(config_file)
          args[args.index('-c') + 1] = config_file

      # explicitly invoke with the current python interpreter
      args.insert(0, sys.executable)

      # remove rebootstrap extension, which is not needed in rebootstrap part
      extension_list = self.buildout['buildout']['extensions'].split()
      extension_list = [q.strip() for q in extension_list if q.strip() != \
          __name__]
      # rerun buildout with only neeeded section to reuse buildout
      # ability to calcuate all dependency
      args.extend([
        # chroot to rebootstrap directory
        'buildout:directory=%s' % self.rebootstrap_directory,
        # install only required section with dependencies
        'buildout:parts=%s' % self.python_section,
        # do not load this extension
        'buildout:extensions=%s' % ' '.join(extension_list),
        # more parameters for building slapos package
        'buildout:rootdir=%s' % self.rebootstrap_directory,
        'buildout:destdir=',
      ])
      self.logger.info('Rerunning buildout to install section %s with '
        'arguments %r.'% (self.python_section, args))
      process = subprocess.Popen(args)
      process.wait()
      if process.returncode != 0:
        raise zc.buildout.UserError('Error during installing python '
          'provision section.')
    if not os.path.exists(self.wanted_python):
      raise zc.buildout.UserError('Section %r directed to python executable:\n'
          '%r\nUnfortunately even after installing this section executable was'
          ' not found.\nThis is section responsibility to provide python (eg. '
          'by compiling it).' % (self.python_section, self.wanted_python))
