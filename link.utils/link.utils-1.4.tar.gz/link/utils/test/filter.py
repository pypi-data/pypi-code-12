# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from unittest import main

from link.utils.filter import get_field, set_field, del_field, Filter, Mangle
from datetime import datetime


class TestField(UTCase):
    def setUp(self):
        self.document = {
            'foo': {
                'bar': 'baz'
            }
        }

    def test_get(self):
        got = get_field('foo.bar', self.document)
        self.assertEqual(got, 'baz')

    def test_set(self):
        set_field('foo.biz.buz', self.document, 'boz')

        self.assertTrue('biz' in self.document['foo'])
        self.assertTrue('buz' in self.document['foo']['biz'])

        got = self.document['foo']['biz']['buz']
        self.assertEqual(got, 'boz')

    def test_del(self):
        del_field('foo.bar', self.document)

        self.assertTrue('bar' not in self.document['foo'])


class TestFilter(UTCase):
    def test_equal(self):
        f = Filter({'foo': 'bar'})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'foo': 'baz'}
        result = f.match(doc)
        self.assertFalse(result)

    def test_regex(self):
        f = Filter({'foo': {'$regex': 'ba.*'}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'foo': 'baz'}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'foo': 'biz'}
        result = f.match(doc)
        self.assertFalse(result)

    def test_exists(self):
        f = Filter({'foo': {'$exists': True}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {}
        result = f.match(doc)
        self.assertFalse(result)

        f = Filter({'foo': {'$exists': False}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {}
        result = f.match(doc)
        self.assertTrue(result)

    def test_notregex(self):
        f = Filter({'foo': {'$not': 'ba.*'}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'foo': 'baz'}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'foo': 'biz'}
        result = f.match(doc)
        self.assertTrue(result)

    def test_not(self):
        f = Filter({'foo': {'$not': {'$exists': True}}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {}
        result = f.match(doc)
        self.assertTrue(result)

        f = Filter({'foo': {'$not': {'$exists': False}}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {}
        result = f.match(doc)
        self.assertFalse(result)

    def test_lt(self):
        f = Filter({'i': {'$lt': 5}})

        doc = {'i': 1}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 6}
        result = f.match(doc)
        self.assertFalse(result)

    def test_lte(self):
        f = Filter({'i': {'$lte': 5}})

        doc = {'i': 1}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 6}
        result = f.match(doc)
        self.assertFalse(result)

    def test_gt(self):
        f = Filter({'i': {'$gt': 5}})

        doc = {'i': 6}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 1}
        result = f.match(doc)
        self.assertFalse(result)

    def test_gte(self):
        f = Filter({'i': {'$gte': 5}})

        doc = {'i': 6}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 1}
        result = f.match(doc)
        self.assertFalse(result)

    def test_ne(self):
        f = Filter({'i': {'$ne': 5}})

        doc = {'i': 1}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertFalse(result)

    def test_eq(self):
        f = Filter({'i': {'$eq': 5}})

        doc = {'i': 1}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertTrue(result)

    def test_in(self):
        f = Filter({'foo': {'$in': ['bar', 'baz']}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'foo': 'baz'}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'foo': 'biz'}
        result = f.match(doc)
        self.assertFalse(result)

    def test_nin(self):
        f = Filter({'foo': {'$nin': ['bar', 'baz']}})

        doc = {'foo': 'bar'}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'foo': 'baz'}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'foo': 'biz'}
        result = f.match(doc)
        self.assertTrue(result)

    def test_all(self):
        f = Filter({'i': {'$all': [1, 2, 3]}})

        doc = {'i': [1, 2, 3, 4]}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': [1, 2, 4]}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 1}
        result = f.match(doc)
        self.assertFalse(result)

    def test_and(self):
        f = Filter({'$and': [
            {'foo': {'$exists': True}},
            {'i': {'$lt': 5}}
        ]})

        doc = {'foo': 'bar', 'i': 0}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'foo': 'bar', 'i': 5}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 0}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertFalse(result)

    def test_or(self):
        f = Filter({'$or': [
            {'foo': {'$exists': True}},
            {'i': {'$lt': 5}}
        ]})

        doc = {'foo': 'bar', 'i': 0}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'foo': 'bar', 'i': 5}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 0}
        result = f.match(doc)
        self.assertTrue(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertFalse(result)

    def test_nor(self):
        f = Filter({'$nor': [
            {'foo': {'$exists': True}},
            {'i': {'$lt': 5}}
        ]})

        doc = {'foo': 'bar', 'i': 0}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'foo': 'bar', 'i': 5}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 0}
        result = f.match(doc)
        self.assertFalse(result)

        doc = {'i': 5}
        result = f.match(doc)
        self.assertTrue(result)


class TestMangle(UTCase):
    def test_inc(self):
        m = Mangle({'$inc': {'i': 5}})

        doc = {'i': 0}
        got = m(doc)
        self.assertEqual(got['i'], 5)

    def test_mul(self):
        m = Mangle({'$mul': {'i': 5}})

        doc = {'i': 1}
        got = m(doc)
        self.assertEqual(got['i'], 5)

    def test_rename(self):
        m = Mangle({'$rename': {'foo': 'bar'}})

        doc = {'foo': 'baz'}
        got = m(doc)

        self.assertTrue('foo' not in got)
        self.assertTrue('bar' in got)
        self.assertEqual(got['bar'], 'baz')

    def test_set(self):
        m = Mangle({'$set': {'foo': 'bar'}})

        doc = {}
        got = m(doc)

        self.assertTrue('foo' in got)
        self.assertEqual(got['foo'], 'bar')

    def test_unset(self):
        m = Mangle({'$unset': {'foo': 1}})

        doc = {'foo': 'bar'}
        got = m(doc)

        self.assertTrue('foo' not in got)

    def test_min(self):
        m = Mangle({'$min': {'i': 5}})

        doc = {'i': 1}
        got = m(doc)
        self.assertEqual(got['i'], 1)

        doc = {'i': 10}
        got = m(doc)
        self.assertEqual(got['i'], 5)

    def test_max(self):
        m = Mangle({'$max': {'i': 5}})

        doc = {'i': 1}
        got = m(doc)
        self.assertEqual(got['i'], 5)

        doc = {'i': 10}
        got = m(doc)
        self.assertEqual(got['i'], 10)

    def test_currentDate(self):
        m = Mangle({
            '$currentDate': {
                'foo': {'$type': 'date'},
                'bar': {'$type': 'timestamp'},
                'baz': True
            }
        })

        doc = {}
        got = m(doc)

        self.assertTrue('foo' in got)
        self.assertTrue('bar' in got)
        self.assertTrue('baz' in got)

        self.assertTrue(isinstance(got['foo'], datetime))
        self.assertTrue(isinstance(got['bar'], float))
        self.assertTrue(isinstance(got['baz'], datetime))

    def test_addToSet(self):
        m = Mangle({
            '$addToSet': {
                'i': 4,
                'foo': {'$each': ['bar', 'baz']}
            }
        })

        doc = {'i': [1, 2, 3]}
        got = m(doc)

        self.assertTrue(1 in got['i'])
        self.assertTrue(2 in got['i'])
        self.assertTrue(3 in got['i'])
        self.assertTrue(4 in got['i'])
        self.assertTrue('foo' in got)
        self.assertTrue('bar' in got['foo'])
        self.assertTrue('baz' in got['foo'])

    def test_pop(self):
        m = Mangle({
            '$pop': {
                'i': 1,
                'j': -1
            }
        })

        doc = {
            'i': [1, 2],
            'j': [1, 2]
        }
        got = m(doc)

        self.assertTrue(1 not in got['i'])
        self.assertTrue(2 in got['i'])
        self.assertTrue(1 in got['j'])
        self.assertTrue(2 not in got['j'])

    def test_pull(self):
        m = Mangle({
            '$pull': {
                'foo': 'bar',
                'bar': {
                    'i': {'$gt': 5}
                }
            }
        })

        doc = {
            'foo': ['bar', 'baz'],
            'bar': [
                {'i': 1},
                {'i': 2},
                {'i': 3},
                {'i': 4},
                {'i': 5},
                {'i': 6},
                {'i': 7}
            ]
        }
        got = m(doc)

        self.assertTrue('bar' not in got['foo'])
        self.assertTrue('baz' in got['foo'])

        for item in got['bar']:
            self.assertTrue(item['i'] <= 5)

    def test_pullAll(self):
        m = Mangle({
            '$pullAll': {
                'foo': ['bar', 'baz']
            }
        })

        doc = {
            'foo': ['bar', 'baz', 'biz']
        }
        got = m(doc)

        self.assertTrue('bar' not in got['foo'])
        self.assertTrue('baz' not in got['foo'])
        self.assertTrue('biz' in got['foo'])

    def test_push(self):
        m = Mangle({
            '$push': {
                'foo': 'bar',
                'bar': {
                    '$each': ['baz', 'biz']
                },
                'baz': {
                    '$each': ['biz', 'buz'],
                    '$sort': -1
                },
                'biz': {
                    '$each': ['biz', 'buz'],
                    '$sort': 1
                },
                'buz': {
                    '$each': [{'i': 1}, {'i': 5}],
                    '$sort': {
                        'i': 1
                    }
                },
                'boz': {
                    '$each': ['buz', 'boz'],
                    '$slice': 1
                }
            }
        })

        doc = {
            'bar': ['bar'],
            'baz': ['foo'],
            'biz': ['foo'],
            'buz': [{'i': 8}, {'i': 4}]
        }
        got = m(doc)

        self.assertTrue('foo' in got)
        self.assertTrue('bar' in got['foo'])

        self.assertTrue('bar' in got['bar'])
        self.assertTrue('baz' in got['bar'])
        self.assertTrue('biz' in got['bar'])

        self.assertEqual(got['baz'], ['foo', 'buz', 'biz'])
        self.assertEqual(got['biz'], ['biz', 'buz', 'foo'])

        prev = None

        for item in got['buz']:
            if prev is not None:
                self.assertTrue(prev['i'] <= item['i'])

            prev = item

        self.assertTrue('boz' in got)
        self.assertTrue('buz' in got['boz'])
        self.assertTrue('boz' not in got['boz'])
        self.assertEqual(len(got['boz']), 1)

    def test_bit(self):
        m = Mangle({
            '$bit': {
                'foo': {'and': 4},
                'bar': {'or': 4},
                'baz': {'xor': 4},
                'biz': {'and': 4},
                'buz': {'or': 4},
                'boz': {'xor': 4}
            }
        })

        doc = {
            'foo': 3,
            'bar': 3,
            'baz': 3
        }
        got = m(doc)

        self.assertEqual(got['foo'], 0)
        self.assertEqual(got['bar'], 7)
        self.assertEqual(got['baz'], 7)

        self.assertTrue('biz' in got)
        self.assertEqual(got['biz'], 0)
        self.assertTrue('buz' in got)
        self.assertEqual(got['buz'], 4)
        self.assertTrue('boz' in got)
        self.assertEqual(got['boz'], 4)


if __name__ == '__main__':
    main()
