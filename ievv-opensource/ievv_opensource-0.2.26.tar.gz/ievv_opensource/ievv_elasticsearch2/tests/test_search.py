from pprint import pprint

import elasticsearch_dsl
from django import test
from elasticsearch_dsl.connections import connections

from ievv_opensource import ievv_elasticsearch2


class PersonSearch(ievv_elasticsearch2.Search):
    def query_name(self, name):
        return self.query('match', name=name)


class FancyPersonSearch(ievv_elasticsearch2.Search):
    def query_all(self, text):
        return self.query(ievv_elasticsearch2.Q('match', name=text) | ievv_elasticsearch2.Q('match', description=text))


class PersonDocType(ievv_elasticsearch2.DocType):
    objects = PersonSearch()
    fancysearch = FancyPersonSearch()

    name = elasticsearch_dsl.String()
    description = elasticsearch_dsl.String()

    class Meta:
        index = 'main'


class TestSearch(test.TestCase):
    def setUp(self):
        self.es = connections.get_connection()
        self.es.indices.delete(index='_all')
        self.es.indices.flush(index='_all')

    def test_raw(self):
        self.es.index(index='test', doc_type='person', id=1, body={
            'name': 'Peter'
        })
        self.es.indices.flush()
        search = ievv_elasticsearch2.Search()\
            .query('match', name='Peter')

        result = search.execute()
        print(type(result))
        pprint(result)

    def test_doctype(self):
        PersonDocType.init()
        person = PersonDocType(name='Peter',
                               description='The Pan')
        person.save()
        self.es.indices.flush()

        # search = ievv_elasticsearch2.Search()\
        #     .query('match', name='Peter')
        #
        # result = search.execute()

        search = PersonDocType.objects.query_name(name='Peter')
        result = search.execute()
        pprint(result)

        search = PersonDocType.fancysearch.query_all(text='Pan')
        result = search.execute()
        pprint(result)

        search = PersonDocType.search().query('match', name='Peter')
        result = search.execute()
        pprint(result)

        # search = ievv_elasticsearch2.Search().query('match', name='Peter')
        # pprint(search.to_dict())
        # result = search.execute()
        # pprint(result)

    def test_get_error(self):
        PersonDocType.init()
        person = PersonDocType(name='Peter',
                               description='The Pan')
        person.save()
        self.es.indices.flush()
        with self.assertRaises(ievv_elasticsearch2.exceptions.NotFoundError):
            PersonDocType.get(id=10)
