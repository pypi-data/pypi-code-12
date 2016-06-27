#!/usr/bin/env python

from voluptuous import Schema

import Constants
import json
import os
import ShellCommand
import yaml

class Inspection(object):

  def __init__(self, inspection_directory):
    self.inspection_directory = inspection_directory
    # Deal in absolutes
    if( not os.path.isabs(inspection_directory) ):
      self.inspection_directory = os.path.expanduser(inspection_directory)

    self.basename = os.path.basename(self.inspection_directory)
    self.name = ''
    self.structure_file = os.path.join(self.inspection_directory, Constants.INSPECTION_STRUCTURE_FILE)
    self.executable_file = None
    self.inspection_result = None

    self.structure = {}

    # Discovery and verification of inspection
    # Log debug: checking inspection <basename>[path]
    if( os.path.exists(self.inspection_directory) ):
      if( not os.path.isdir(self.inspection_directory) ):
        # Log error: insepction path is not a directory
        raise Exception('Kickstand inspection path [%s] is not a directory' % self.inspection_directory)
    else:
      # Log error: inspection path does not exist
      raise Exception('Kickstand inspection path [%s] does not exists' % self.inspection_directory)

    # Sturcutre file discovery and validation
    if( os.path.exists(self.structure_file) ):
      if( os.path.isfile(self.structure_file) ):
        # Log debug: inspection structure file found
        if( os.access(self.structure_file, os.R_OK) ):
          # Log debug: inspection structure file readable
          pass
        else:
          # Log error: inavlid permission to read inspection structure file
          raise Exception('Cannot read Kickstand inspection %s structure file [%s]' % (self.basename, self.structure_file))
      else:
        # Log error: inspection structure file path is not a file
        raise Exception('Kickstand inspection structure file path [%s] is not a file' % self.structure_file)
    else:
      # Log error: inspection structure file not found
      raise Exception('Kickstand inspection structure file [%s] not found' % self.structure_file)

    # Executable inspection file discovery and validation
    inspection_files = os.listdir(self.inspection_directory)
    executable_files = []
    for efile in inspection_files:
      if( Constants.INSPECTION_EXECUTABLE_FILE_BASENAME in efile ):
        executable_files.append(efile)

    if( len(executable_files) == 0 ):
      # Log error: Kickstand inspection <basename> inspect file not found
      raise Exception('Kicktand inspection %s inspect file not found' % self.basename)
    elif( len(executable_files) > 1 ):
      # Log error: Found multiple inspect files in inspection <basename>
      raise Exception('Kickstand inspection %s has multiple inspect files' % self.basename)

    self.executable_file = os.path.join(self.inspection_directory, executable_files[0])

    # Log info: Kickstand inspection <basename> inspect file found at <inspectfile>

    if( os.access(self.executable_file, os.X_OK) ):
      # Log debug: Kickstand inspection inspect file is executable
      pass
    else:
      # Log warning: Kickstand inspection inspect file is not executable
      pass

    # Log debug: inspection <basename>[path] check complete

    # Check structure file against kickstand server for defined components
    # Log debug: checking components defined in structure file against server
    structure_file_handle = file(self.structure_file, 'r')
    structure_yaml_string = ('\n').join(structure_file_handle.readlines())
    
    structure_dict = yaml.load(structure_yaml_string)
    self.name = structure_dict['name']

    for category in structure_dict['categories']:
      catshort = category['shortname']
      if( catshort not in self.structure ):
        self.structure[catshort] = {}
      self.structure[catshort]['name'] = category['name']
      self.structure[catshort]['description'] = category['description'].strip('\n') if 'description' in category else ''
      self.structure[catshort]['components'] = {}
      for component in category['components']:
        compshort = component['shortname']
        if( compshort not in self.structure[catshort]['components'] ):
          self.structure[catshort]['components'][compshort] = {}
        self.structure[catshort]['components'][compshort]['name'] = component['name']
        self.structure[catshort]['components'][compshort]['description'] = component['description'].strip('\n') if 'description' in component else ''
        self.structure[catshort]['components'][compshort]['has_many'] = component['hasmanyproperties'] if 'hasmanyproperties' in component else False
        self.structure[catshort]['components'][compshort]['properties'] = {}
        for prop in component['properties']:
          propshort = prop['shortname']
          if( propshort not in self.structure[catshort]['components'][compshort]['properties'] ):
            self.structure[catshort]['components'][compshort]['properties'][propshort] = {}
          self.structure[catshort]['components'][compshort]['properties'][propshort]['name'] = prop['name']
          self.structure[catshort]['components'][compshort]['properties'][propshort]['description'] = prop['description'].strip('\n') if 'description' in prop else ''
          self.structure[catshort]['components'][compshort]['properties'][propshort]['type'] = prop['type'] if 'type' in prop else 'string'
          self.structure[catshort]['components'][compshort]['properties'][propshort]['default'] = prop['default'] if 'default' in prop else ''
          self.structure[catshort]['components'][compshort]['properties'][propshort]['required'] = prop['required'] if 'required' in prop else False

    # Log debug: Loaded inspection structure

  def inspect(self):
    output, error, returncode = ShellCommand.execute('%s' % self.executable_file)

    if( returncode != 0 ):
      raise Exception('Kickstand inspection %s failed to inspect the machine' % self.basename)

    if( len(error) > 0 ):
      # Print output into log
      pass

    inspection_result = json.loads(output)

    for category in inspection_result:
      if( category not in self.structure ):
        raise Exception('Kickstand inspection %s returned category %s which is not defined by the structure' % (self.basename, category))

      for component in inspection_result[category]:
        if( component not in self.structure[category]['components'] ):
          raise Exception('Kickstand inspection %s returned component %s which is not defined under category %s by the structure' % (self.basename, component, category))

        for prop in inspection_result[category][component]:
          if( prop not in self.structure[category]['components'][component]['properties'] ):
            raise Exception('Kickstand inspection %s returned property %s which is not defined under component %s under category %s by the structure' % (self.basename, prop, component, category))

    self.inspection_result = inspection_result
    return inspection_result

  def getBasename(self):
    return self.basename

  def getName(self):
    return self.name

  def getResults(self):
    return self.inspection_result

  def getStructure(self):
    return self.structure
