# encoding: utf-8

from affinitic.caching.memcached import cache
from lovely.memcached.event import InvalidateCacheEvent
from lovely.memcached.interfaces import IMemcachedClient
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from time import sleep
from zope.component import getUtility
from zope.component.testlayer import ZCMLFileLayer
from zope.event import notify

import affinitic.caching
import unittest2


def cache_key(fun, self, first, second):
    return (first, second)


class B(object):
    value = None


class User(object):
    pass


class A(object):
    def __init__(self):
        self.calculationCount = 0

    @cache(cache_key, dependencies=['Einstein'])
    def sum(self, a, b):
        self.calculationCount += 1
        return a+b

    @cache(cache_key, dependencies=['Einstein'])
    def sumObj(self, a, b):
        self.calculationCount += 1
        bObj = B()
        bObj.value = a+b
        return bObj


class C(object):
    def __init__(self):
        self.calculationCount = 0

    @cache(cache_key, dependencies=['Einstein'], lifetime=3)
    def sum(self, a, b):
        self.calculationCount += 1
        return a+b

zcml_file_layer = ZCMLFileLayer(
    affinitic.caching,
    'testing.zcml')


queryCount = 0


class TestMemcached(unittest2.TestCase):
    layer = zcml_file_layer

    def tearDown(self):
        memclient = getUtility(IMemcachedClient)
        memclient.invalidateAll()

    def test_caching_and_dependencies(self):
        a = A()
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(1, a.calculationCount)
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(1, a.calculationCount)

    def test_invalidate_dependencies(self):
        a = A()
        memclient = getUtility(IMemcachedClient)
        memclient.invalidate(raw=True, dependencies=['Einstein'])
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(1, a.calculationCount)
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(1, a.calculationCount)

    def test_calling_event(self):
        a = A()
        notify(InvalidateCacheEvent(raw=True, dependencies=['Einstein']))
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(1, a.calculationCount)

    def test_sqlalchemy(self):
        metadata = MetaData()
        engine = create_engine('sqlite:///:memory:')
        users = Table('testusers', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('name', String(40)),
                      Column('fullname', String(100)),
                      )
        metadata.create_all(engine)
        mapper(User, users)
        user1 = User()
        user1.id = 1
        user1.name = 'Einstein'
        user1.fullname = 'Albert Einstein'
        session = sessionmaker(bind=engine, autoflush=False)()
        session.save(user1)
        session.flush()

        def cache_key_maker(fun, self):
            return ()

        class QueryMaker(object):

            @cache(cache_key_maker, dependencies=['Einstein'])
            def getAllUsers(self):
                global queryCount
                queryCount += 1
                return session.query(User).all()

        queryMaker = QueryMaker()
        users = queryMaker.getAllUsers()
        self.assertEqual(1, len(users))
        self.assertEqual('Albert Einstein', users[0].fullname)
        self.assertEqual(1, queryCount)
        queryMaker = QueryMaker()
        users = queryMaker.getAllUsers()
        self.assertEqual(1, queryCount)
        self.assertEqual(1, len(users))
        albert = users[0]
        albert.fullname = 'Alberto Tomba'

        session = sessionmaker(bind=engine, autoflush=False,
                               transactional=False)()
        session.save_or_update(albert)
        self.assertEqual(1, queryCount)

        notify(InvalidateCacheEvent(raw=True, dependencies=['Einstein']))
        queryMaker = QueryMaker()
        users = queryMaker.getAllUsers()
        self.assertEqual(1, len(users))
        self.assertEqual(2, queryCount)
        self.assertEqual('Alberto Tomba', users[0].fullname)

    def test_timeout(self):
        a = C()
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(1, a.calculationCount)
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(1, a.calculationCount)
        sleep(4)
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(2, a.calculationCount)
        self.assertEqual(3, a.sum(1, 2))
        self.assertEqual(2, a.calculationCount)
