#!/usr/bin/env python

import Constants
import os

from Inspection import Inspection

class Inspector(object):

  def __init__(self, inspections_directories):
    self.inspections_directories = []
    self.inspections = []
    self.structure = {}
    self.recorded_results = {}

    for directory in inspections_directories:
      if( not os.path.isabs(directory) ):
        directory = os.path.expanduser(directory)
      self.inspections_directories.append(directory)

    for inspections_dir in self.inspections_directories:
      # Log debug: checking inspections configuration
      if( os.path.exists(inspections_dir) ):
        if( not os.path.isdir(inspections_dir) ):
          # Log error: Kickstand inspections path is not a directory
          raise Exception('Kickstand inspections path is not a directory')
      else:
        # Log warning: Kickstand inspections directory does not exist
        try:
          # Log info: creating Kickstand inspections directory (0766)
          os.makedirs(inspections_dir, 0766)
        except OSError as err:
          # Log error: failed to create Kickstand inspections directory
          raise Exception('Failed to create Kickstand inspections directory [%s]: %s' % (inspections_dir, str(err)))

        # Log debug: successfully created Kickstand inspections directory(0766)

      # Log debug: inspections configuration check complete

      # Get inspections
      inspector_dir_list = os.listdir(inspections_dir)
      for name in inspector_dir_list:
        path = os.path.join(inspections_dir, name)
        if( os.path.isdir(path) ):
          self.inspections.append(Inspection(path))
        else:
          # Log warning: name in inspections directory is not a directory
          pass

  def getStructure(self):
    struct = {}
    for inspection in self.inspections:
      struct = self.updateDict(struct, inspection.getStructure())

    return struct

  def inspect(self):
    result = {}
    for inspection in self.inspections:
      result = self.updateDict(result, inspection.inspect())

    return result

  def updateDict(self, dictionary, updated):
    for key, value in updated.iteritems():
      if( key in dictionary and type(value) == type({}) and type(dictionary[key]) == type({}) ):
        dictionary[key] = self.updateDict(dictionary[key], value)
      else:
        dictionary[key] = value
    return dictionary
