#!/usr/bin/env python
"""Toplevel Kickstand Inventory"""

from Machine import Machine
from Category import Category
from Status import Status
from Group import Group

def getMachine(communicator, id=None, hostname=None, fqdn=None):
  """Returns the machine object.

  Input:
    id: integer identifying a machine
    hostname: string identifying the hostname of a machine
    fqdn: string identifying the fully qualified domain name of a machine

  Output:
    Machine: an object representing a machine
  """
  result = None
  if( id is not None and hostname is None and fqdn is None ):
    result = communicator.get('inventory/machines/%s' % id)
  elif( hostname is not None and id is None and fqdn is None ):
    result = communicator.get('inventory/machines/%s' % hostname)
  elif( fqdn is not None and id is None and fqdn is None ):
    result = communicator.get('inventory/machines/%s' % fqdn)
  else:
    raise Exception('Can only pass one of id, hostname, and fqdn.')

  # Check for result error
  machine = Machine(communicator, data=result.json())

  return machine

def getMachines(communicator, fqdn=None):
  """Returns a list of machines from Kickstand. Used for searching and/or
     retrieving multiple machines.

  Input:

  Output:
    list: of Machine objects
      example: [Machine(..), Machine(..)]
  """
  parameters = {}
  if( fqdn is not None ):
    parameters['fqdn'] = fqdn

  machines_response = communicator.get('inventory/machines', params=parameters)
  machines_data = machines_response.json()['data']

  machines = []

  for m in machines_data:
    machines.append(Machine(communicator, data=m))

  return machines

def _getSingleObject(communicator, uri, object_type):
  """Returns a single object retrieved from the server."""
  result = communicator.get(uri)
  obj = object_type(communicator, data=result.json()['data'])
  return obj

def _getMultipleObjects(communicator, uri, object_type):
  """Returns a list of objects retrieved from the server."""
  result = communicator.get(uri)
  objects = result.json()['data']

  obj_list = []
  for o in data:
    obj_list.append(object_type(communicator, data=o))

  return obj_list

def getStatus(communicator, id=None, name=None):
  """Returns a status object.

  Input:
    id: integer identifying a status
    name: string of the short name identifying a status

  Output:
    Status: an object representing a status
  """
  result = None

  if( id is not None and name is None ):
    result = communicator.get('inventory/status/%d' % id)
  elif( name is not None and id is None ):
    result = communicator.get('inventory/status/%s' % name)
  else:
    raise Exception('Can only pass one of id or name.')

  status = Status(communicator, data=result.json())
  return status

def getStatuses(communicator):
  """Returns a list of status objects.

  Input:

  Output:
    list: of Status objects
      example: [Status(..), Status(..)]
  """
  status_response = communicator.get('/inventory/status')
  statuses_data = status_response.json()['data']

  statuses = []
  for status in statuses_data:
    statuses.append(Status(communicator, data=status))

  return statuses
