from pylib import views
from pylib.views import collection, entity
from pylib.views.collection import Collection
from pylib.views.entity import Entity
from pylib.middleware.json import JSONTranslator, RequireJSON

from falcon.testing import TestBase
import falcon as falconry
import json
from marshmallow import Schema
from marshmallow.fields import Int, Str, Date

from pylib.validation.validators import enum



class Person(Schema):
    id = Int()
    firstname = Str(required=True)
    surname = Str(required=True)
    homephone = Str()
    dob = Date()



def good():
    return dict(firstname='Olakunle', surname='Arewa', homephone='07057108351', dob='1993-08-16')


def normal():
    n = good()
    n['firstname'] = 'Daniel'
    return n


def bad():
    return dict(surname='Arewa', homephone='07057108351', dob='1993-08-16')


def params():
    return dict(headers={'Content-Type': 'application/json'}, decode='utf-8')


def process_response(res):
    return json.loads(str(res))


def before_hook(req, resp, res, params):
    print('Before hook')


def after_hook(req, resp):
    print('After hook')

pcoll = Collection('/api/persons', Person(), before=[before_hook], after=[after_hook])
pentity = Entity('/api/persons', 'pid', Person(),
                 before=[views.int_id_hook('pid'), before_hook], after=[after_hook])
persons = []


@collection.create(pcoll)
def create(person):
    persons.append(person)
    return len(persons) - 1


@collection.search(pcoll)
def search(query):
    return persons


@entity.read(pentity)
def read(pid):
    if pid < len(persons):
        return persons[pid]


@entity.update(pentity)
def update(pid, entity):
    if pid < len(persons):
        persons[pid] = entity
        return entity


@entity.delete(pentity)
def delete(pid):
    if pid < len(persons):
        return persons.pop(pid)


class TestCollection(TestBase):

    def before(self):
        self.api = falconry.API(middleware=[RequireJSON(), JSONTranslator()])
        self.good_person = good()
        self.bad_person = bad()
        views.register(pcoll, self.api)

    def test_create(self):
        res = self.simulate_request('/api/persons', method='POST', body=json.dumps(self.good_person), **params())
        res = process_response(res)
        assert self.srmock.status == falconry.HTTP_200
        assert res['id'] == 0

    def test_create_error(self):
        res = self.simulate_request('/api/persons', method='POST', body=json.dumps(self.bad_person), **params())
        res = process_response(res)
        assert self.srmock.status == falconry.HTTP_400


    def test_search(self):
        res = self.simulate_request('/api/persons', method='GET',
                                    query_string='query=Arewa&query_type=firstname', **params())
        res = process_response(res)
        assert self.srmock.status == falconry.HTTP_200
        assert len(res) == 1
        assert res[0]['firstname'] == 'Olakunle'


# Unfortunately we cannot run on test with the orders as they
# have to be ordered and the test runner pytest likes to jump
# around
# class TestEntity(TestBase):

    def before(self):
        self.api = falconry.API(middleware=[RequireJSON(), JSONTranslator()])
        self.good_person = good()
        self.bad_person = bad()
        self.normal_person = normal()
        views.register(pcoll, self.api)
        views.register(pentity, self.api)

#     def test_read(self):
#         res = self.simulate_request('/api/persons/0', method='GET', **params())
#         res = process_response(res)
#         assert self.srmock.status == falconry.HTTP_200
#         assert res['firstname'] == 'Olakunle'

    # def test_edit(self):
    #     res = self.simulate_request('/api/persons/0', method='PUT',
    #                                 body=json.dumps(self.normal_person), **params())
    #     res = process_response(res)
    #     assert self.srmock.status == falconry.HTTP_200
    #     assert res['firstname'] == 'Daniel'

    # def test_delete(self):
    #     res = self.simulate_request('/api/persons/0', method='DELETE', **params())
    #     res = process_response(res)
    #     assert self.srmock.status == falconry.HTTP_200
    #     assert res['firstname'] == 'Olakunle'
    #     res = self.simulate_request('/api/persons', method='GET', **params())
    #     res = process_response(res)
    #     assert self.srmock.status == falconry.HTTP_200
    #     assert len(res) == 0
