
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan as es_scan, bulk as es_bulk
import elasticsearch_dsl as dsl

# ElasticSearch
class ElasticSearchIndex(object):
    def __init__(self, url):
        uri, index = url.split("/", 2)
        self._uri = uri
        self.client = Elasticsearch(uri)
        self.index_name = index

    def use(self, doc_type):
        return Doc(client=self.client,
                                index_name=self.index_name,
                                doc_type=doc_type)

    def delete(self):
        self.client.indices.delete(index=self.index_name, ignore=[400, 404])

class Doc(object):

    def __init__(self, client, index_name, doc_type):
        self.client = client
        self.index_name = index_name
        self.doc_type = doc_type

    def index(self, id, doc, upsert=True, ignore=[404], **kwargs):
        """
        To create or update doc
        :param id: int
        :param doc: dict
        :param upsert: bool
        :param ignore: dict
        :param kwargs:
        :return:
        """
        body = doc
        if upsert:
            body = {
                "doc": doc,
                "doc_as_upsert": True
            }
        return self.client.update(index=self.index_name,
                                  doc_type=self.doc_type,
                                  id=id,
                                  body=body,
                                  ignore=ignore,
                                  **kwargs)

    def delete(self, id, ignore=[404], **kwargs):
        return self.client.delete(index=self.index_name,
                                  doc_type=self.doc_type,
                                  id=id,
                                  ignore=ignore,
                                  **kwargs)

    def get(self, id, **kwargs):
        return self.client.get(index=self.index_name,
                               doc_type=self.doc_type,
                               id=id,
                               **kwargs)

    def create(self, id, doc, **kwargs):
        """
        To create a new index. If it exists, will throw error
        :param id: int
        :param doc: dict
        :param kwargs:
        :return:
        """
        return self.client.create(index=self.index_name,
                                  doc_type=self.doc_type,
                                  id=id,
                                  body=doc,
                                  **kwargs)


    def search(self, *args, **kwargs):
        return dsl.Search(using=self.client,
                          index=self.index_name,
                          doc_type=self.doc_type)

    def delete_all_documents(self):
        scroll = '5m'
        docs = es_scan(self.client,
                       query={},
                       index=self.index_name,
                       doc_type=self.doc_type)
        for d in docs:
            self.delete(id=d["_id"])