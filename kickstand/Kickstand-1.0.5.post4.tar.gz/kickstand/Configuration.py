#!/usr/bin/env python

import configargparse
import Constants

class Configuration(dict):

  def addArguments(self):
    self.config_instance.add('-s', '--server', dest='SERVER', required=True, help='Kickstand server.')

    self.config_instance.add('--inspections-dir', dest='INSPECTIONS_DIRECTORIES',
        action='append', default=[], help='Directory of Kickstand inspections.')
    self.config_instance.add('--no-default-inspections', dest='INSPECTIONS_DONT_USE_DEFAULTS',
        action='store_true', help='Do not use inspections from teh default check directories.')

    self.config_instance.add('--no-sync', dest='NO_SYNC', action='store_true',
        help='Prevent synchronization to the Kickstand server.')
    self.config_instance.add('-q', '--quiet', dest='QUIET', action='store_true',
        help='Prevent the tool from printing information.')

  def __init__(self, overrides={}):
    self.overrides = overrides

    self.config_instance = configargparse.ArgumentParser(prog='kickstand',
        default_config_files=['/etc/kickstand.yaml', '~/.kickstand.yaml'],
        description='Interacts with a Kickstand server')
    self.addArguments()
    self.config = self.config_instance.parse_args()

  def __getattr__(self, key):
    if( key in self.overrides ):
      return self.overrides[key]
    return getattr(self.config, key)

  def __getitem__(self, key):
    if( key in self.overrides ):
      return self.overrides[key]
    return getattr(self.config, key)
