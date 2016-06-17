#!/usr/bin/env python

from .. import Communicator

class Status(object):
  """Object representing a Status from the Kickstand server."""

  def __init__(self, communicator, id=None, short_name=None, data=None):
    self._id = None
    self._created_at = None
    self._deleted_at = None
    self._updated_at = None

    self.short_name = None
    self.name = None
    self.description = None

    self._communicator = communicator
    self._modified = False

    if( data is not None ):
      self._populate(data)

  def __getitem__(self, key):
    if( key == 'id' ):
      return self._id
    elif( key == 'name' ):
      return self.name
    elif( key == 'short_name' ):
      return self.short_name
    elif( key == 'description' ):
      return self.description
    elif( key == 'created_at' ):
      return self._created_at
    elif( key == 'updated_at' ):
      return self._updated_at
    elif( key == 'deleted_at' ):
      return self._deleted_at
    else:
      raise KeyError('%s' % key)

  def __setitem__(self, key, value):
    if( key in ['id', 'created_at', 'updated_at', 'deleted_at'] ):
      raise KeyError('%s cannot be modified' % key)
    elif( key == 'name' ):
      if( type(value) != type('') and type(value) != type(u'') ):
        raise TypeError('Value for key %s is not type string' % key)
      if( value != self.name ):
        self.name = value
        self._modified = True
    elif( key == 'short_name' ):
      if( type(value) != type('') and type(value) != type(u'') ):
        raise TypeError('Value for key %s is not type string' % key)
      if( value != self.short_name ):
        self.short_name = value
        self._modified = True
    elif( key == 'description' ):
      if( type(value) != type('') and type(value) != type(u'') ):
        raise TypeError('Value for key %s is not type string' % key)
      if( value != self.description ):
        self.description = value
        self._modified = True
    else:
      raise KeyError('%s' % key)

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
    self.name = data['name']
    self.short_name = data['short_name']
    self.description = data['description']

  def _data(self):
    data_dict = {
      'id':          self._id,
      'name':        self.name,
      'short_name':  self.short_name,
      'description': self.description,
    }

    if( self._id is not None ):
      data_dict['id'] = self._id

    return data_dict

  def commit(self):
    if( not self._modified ):
      return None

    result = None
    if( not self.isCreated() ):
      result = self._communicator.post('/inventory/status',
          data=self._data())
    else:
      result = self._communicator.put('/inventory/status/%d' % self._id,
          data=self._data())

    if( result.status_code == 201 or result.status_code == 204 ):
      self.populate(result.json())
    else:
      raise Exception('%s: %s' % (result.status_code, result.text))

