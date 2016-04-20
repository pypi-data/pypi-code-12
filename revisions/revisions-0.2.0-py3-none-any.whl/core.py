#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Revisions
import requests
import hashlib
import pymongo
import pickle
import bson.binary

from functools import wraps
from datetime import timedelta, datetime

try:
  from unittest import mock
except ImportError:
  import mock


class RevisionCollection(object):
  '''Dictionary interface for Revisions in MongoDB.
  '''

  def __init__(self, db, resolution=timedelta(minutes=1), **kwa):
    ''''''
    self._resolution = resolution
    self._connection = pymongo.MongoClient(**kwa)
    self._db = self._connection[db]
    self._collection = self._db['revisions']

  def __get_rev(self, key, version, **kwa):
    '''Obtain particular version of the doc at key.'''
    if '_doc' in kwa:
      doc = kwa['_doc']
    else:
      if type(version) is int:
        if version == 0:
          order = pymongo.ASCENDING
        elif version == -1:
          order = pymongo.DESCENDING
        doc = self._collection.find_one({'k': key}, sort=[['d', order]])
      elif type(version) is datetime:
        ver = self.__round_time(version)
        doc = self._collection.find_one({'k': key, 'd': ver})

    if doc is None:
      raise KeyError('Supplied key `{0}` or version `{1}` does not exist'
          .format(key, str(version)))

    coded_val = doc['v']
    return pickle.loads(coded_val)

  def __round_time(self, dt):
    """Round a datetime object to a multiple of a timedelta
    dt : datetime.datetime object, default now.
    """
    round_to = self._resolution.total_seconds()
    seconds  = (dt - dt.min).seconds
    rounding = (seconds + round_to / 2) // round_to * round_to
    return dt + timedelta(0, rounding - seconds, -dt.microsecond)

  def __get_revs(self, key, version):
    start = self.__round_time(version.start or datetime.min)
    stop = self.__round_time(version.stop or datetime.max)

    if start > stop:
      raise ValueError('Supplied range is incorrect')

    objs = self._collection.find(
        {'k': key, 'd': {'$gte': start, '$lt': stop}},
        sort=[['d', pymongo.ASCENDING]])

    for obj in objs:
      yield self.__get_rev(key=None, version=None, _doc=obj)

  def __len__(self):
    return self._collection.count()

  def __getitem__(self, _key):
    '''Obtain Revisions or Iterables.

    Obtain specific revisions:
      >>> obj[key]      # Return the most recent revision
      >>> obj[key, -1]  # Return the most recent revision
      >>> obj[key, 0]   # Return the oldest available revision
      >>> obj[key, date(...)]   # Return the revision on the supplied date

    Obtain iterables:
      - Return an iterator which yields all revs.
        >>> obj[key, :]
      - Return an iterator which yields the revisions between supplied dates.
        >>> obj[key, date(...):]
        >>> obj[key, :date(...)]
        >>> obj[key, date(...):date(...)]
    '''
    if type(_key) is tuple and len(_key) == 2:
      key, revision = _key
    elif type(_key) is str:
      key = _key
      revision = -1
    else:
      raise KeyError('Unexpected key type')
    if type(key) is not str:
      raise KeyError('Invalid Key Format')

    if type(revision) is slice:
      return self.__get_revs(key, revision)
    elif type(revision) in [int, datetime]:
      return self.__get_rev(key, revision)
    else:
      raise KeyError('Unexpected revision range(s)')

  def __setitem__(self, key, value):
    if not type(key) is str:
      raise KeyError('Invalid Key. Expected a string.')
    coded_val = pickle.dumps(value)
    self._collection.update_one(
      {
        'k': key,
        'd': self.__round_time(datetime.now())
      },
      {
        '$set': {'v': coded_val}
      },
      upsert=True)

  def __delitem__(self, key):
    self._collection.delete_many({'k': key})

  def __iter__(self):
    for k in self._collection.distinct('k'):
      yield k, self.__get_rev(key=k, version=-1)

  def __contains__(self, key):
    return self._collection.count({'k': key}) > 0


class RequestsMock(object):
  '''
  '''

  def __init__(self, db, **kwa):
    '''
    '''
    self.__request_org = requests.request
    self.revisions = RevisionCollection(db, **kwa)

  def __enter__(self):
    self.start()
    return self

  def __exit__(self, *args):
    self.stop()

  def _hashkey(self, method, url, **kwa):
    '''Find a hash value for the linear combination of invocation methods.
    '''
    to_hash = ''.join([str(method), str(url),
        str(kwa.get('data', '')),
        str(kwa.get('params', ''))
    ])
    return hashlib.md5(to_hash.encode()).hexdigest()

  def __request_patch(self, method, url, **kwa):
    key = self._hashkey(method, url, **kwa)

    try:
      response = self.revisions[key]
      cached = True
    except KeyError:
      response = self.__request_org(method, url, **kwa)
      self.revisions[key] = response
      cached = False
    finally:
      self.callback(method, url, cached, response)
      return response

  @property
  def callback(self):
    try:
      return self.__callback
    except AttributeError:
      return lambda *x: None

  @callback.setter
  def callback(self, func):
    self.__callback = func

  def start(self):
    def delegate(*a, **kwa):
      return self.__request_patch(*a, **kwa)

    self._patcher = mock.patch('requests.api.request', delegate)
    self._patcher.start()

  def stop(self):
    self._patcher.stop()

  def __call__(self):
    pass


def activate(db):
  req_mock = RequestsMock(db=db)
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      with req_mock:
        return func(_rv=req_mock, *args, **kwargs)
    return wrapper
  return decorator
