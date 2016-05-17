#!/usr/bin/env python

from .. import Communicator

import Category
import Status
import Group

class Machine(object):
  """Object representing a Machine from the Kickstand server."""

  def __init__(self, communicator, id=None, host=None, data=None):
    self._id = None
    self._created_at = None
    self._updated_at = None
    self._deleted_at = None
    self._host = None

    self.fqdn = None
    self.status = None
    self.group = None
    self.categories = None
    self.properties = None

    self._communicator = communicator
    self._modified = False

    if( data is not None ):
      self._populate(data)

  def keys(self):
    return ['host', 'fqdn', 'status', 'group', 'categories', 'properties',
        'created_at', 'updated_at', 'deleted_at']

  def __getitem__(self, key):
    if( key == 'host' ):
      return self._host
    elif( key == 'fqdn' ):
      return self.fqdn
    elif( key == 'status' ):
      return self.status
    elif( key == 'group' ):
      return self.group
    elif( key == 'id' ):
      return self._id
    elif( key == 'categories' ):
      return list(self.categories)
    elif( key == 'properties' ):
      return list(self.properties)
    elif( key == 'created_at' ):
      return self._created_at
    elif( key == 'updated_at' ):
      return self._updated_at
    elif( key == 'deleted_at' ):
      return self._deleted_at
    else:
      raise KeyError('%s' % key)

  def __setitem__(self, key, value):
    if( key in ['created_at', 'updated_at', 'deleted_at', 'id', 'host', 'categories', 'properties'] ):
      raise KeyError('%s cannot be modified' % key)
    elif( key == 'fqdn' ):
      if( type(value) != type('') and type(value) != type(u'') ):
        raise TypeError('Value for key %s is not type string' % key)
      if( self.fqdn != value ):
        self.fqdn = value
        self.host = self.fqdn.split('.')[0]
        self._modified = True
    elif( key == 'status' ):
      if( type(value) != Status ):
        raise TypeError('Value for key %s is not type Status' % key)
      if( self.status != value ):
        self.status = value
        self._modified = True
    elif( key == 'group' ):
      if( type(value) != Group ):
        raise TypeError('Value for key %s is not type Group' % key)
      if( self.group != value ):
        self.group = value
        self._modified = True
    else:
      raise KeyError('%s' % key)

  def addCategory(self, category):
    if( type(category) != Category ):
      raise TypeError('Category provided is not type Category')
    else:
      try:
        self._categories.index(category)
      except ValueError:
        self._categories.append(category)
        self._modified = True

  def removeCategory(self, category):
    if( type(category) != Category ):
      raise TypeError('Category provided is not type Category')
    else:
      try:
        self._categories.remove(category)
        self._modified = True
      except ValueError:
        pass

  def isCreated(self):
    return self._created_at is not None

  def isUpdated(self):
    return not self._modified

  def isDeleted(self):
    return self._deleted_at is not None

  def delete(self):
    pass

  def _populate(self, data):
    self._id = data['id']
    self._created_at = data['created_at']
    self._updated_at = data['updated_at']
    self._deleted_at = data['deleted_at']
    self.fqdn = data['fqdn']
    self._host = data['fqdn'].split('.')[0]
    self.status = data['status']
    self.group = data['group']
    self.categories = data['categories']

  def _data(self):
    data_dict = {
        'fqdn': self.fqdn,
        'status': 1,
        'group': 1,
        'categories': [],
    }

    if( self.status is not None ):
      data_dict['status'] = self.status['id']

    if( self.group is not None ):
      data_dict['group'] = self.group['id'],

    if( self.categories is not None ):
      for category in self.categories:
        data_dict['categories'].append(category['id'])

    if( self._id is not None ):
      data_dict['id'] = self._id

    return data_dict

  def commit(self):
    if( not self._modified ):
      return None

    result = None
    if( not self.isCreated() ):
      result = self._communicator.post('/inventory/machines',
          data=self._data())
    else:
      result = self._communicator.patch('/inventory/machines/%d' % self._id,
          data=self._data())

    if( result.status_code == 201 or result.status_code == 204 ):
      new_id = result.json()['id']
      self._populate(self._communicator.get('inventory/machines/%d' % new_id).json())
    else:
      raise Exception('%s: %s' % (result.status_code, result.text))

