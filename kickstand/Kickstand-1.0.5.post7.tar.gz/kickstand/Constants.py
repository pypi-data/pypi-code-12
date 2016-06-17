#!/usr/bin/env python

from voluptuous import All, Optional, Required, Schema

class __constants__(object):

  INSPECTIONS_DEFAULT_DIRECTORIES = [
      '/opt/kickstand/inspections',       # Program added inspections
      '/usr/local/kickstand/inspections', # Administrator added inspections
  ]
  INSPECTION_STRUCTURE_FILE = 'structure.yaml'
  INSPECTION_EXECUTABLE_FILE_BASENAME = 'inspect'

  INSPECTION_STRUCTURE_VALIDATION_SCHEMA = {
    Required('name'): str,
    Required('categories'): All(list, [
      lambda value:
        Schema(All(dict, {
          Required('name'): str,
          Required('shortname'): str,
          Optional('description'): str,
          Required('components'): All(list, [
            lambda value:
              Schema(All(dict, {
                Required('name'): str,
                Required('shortname'): str,
                Optional('description'): str,
                Optional('hasmanyproperties'): bool,
                Required('properties'): All(list, [
                  lambda value:
                    Schema(All(dict, {
                      Required('name'): str,
                      Required('shortname'): str,
                      Optional('description'): str,
                      Optional('type'): str,
                      Optional('default'): str,
                      Optional('required'): bool,
                    }))(value)
                  ]
                ),
              }))(value)
            ]
          ),
        }))(value)
      ]
    ),
  }

  def __setattr__(self, name, value):
    raise Exception('Cannot modify constants')

import sys
sys.modules[__name__] = __constants__()
