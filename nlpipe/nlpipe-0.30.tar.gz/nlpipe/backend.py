"""
Useful functions for communication with elastic

NLPipe assumes that raw texts are stored in an elastic index (see esconfig).
If multiple fields are specified, and/or a field contains multiple results,
they are joined with empty lines in between (e.g. "\n\n".join)

Results are stored in a separate document type per module (version), and are assumed to have the form:
{id: <id>,
 pipeline: [{module: <module>, version: <version>, 
            input_type: <doctype>, input_fields: [<fields>] (raw input only),
            begin_time: <time>, end_time: <time>}]
 result: <result>}
"""

import datetime

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan

from . import esconfig
from .document import Document

_es = Elasticsearch([{"host": esconfig.ES_HOST, "port": esconfig.ES_PORT}])

_CHECKED_MAPPINGS = set()

def set_esconfig(host, port):
    """
    Set the (global) es config
    """
    global _es
    _es = Elasticsearch([{"host": host, "port": int(port)}])

def _check_mapping(doc_type):
    if doc_type not in _CHECKED_MAPPINGS:
        index = esconfig.ES_RESULT_INDEX
        if not _es.indices.exists_type(index=index, doc_type=doc_type):
            mapping = {doc_type: esconfig.ES_MAPPING}
            if not _es.indices.exists(index):
                _es.indices.create(index)
            _es.indices.put_mapping(index=index, doc_type=doc_type, body=mapping)
        _CHECKED_MAPPINGS.add(doc_type)

def get_input_fields(id, fields):
    res = _es.get(index=esconfig.ES_INPUT_INDEX,
                  doc_type=esconfig.ES_INPUT_DOCTYPE,
                  id=id, fields=fields)
    return res['fields']
        
def get_input(id):
    input_type = esconfig.ES_INPUT_DOCTYPE,
    input_fields = esconfig.ES_INPUT_FIELDS
    fields = get_input_fields(id, input_fields)
    text = "\n\n".join("\n\n".join(fields[f]) for f in input_fields if f in fields)
    return Document(id, [], text, input_type, input_fields)

def get_input_ids(query, limit=None):
    """Get the ids of existing input documents that match a query"""
    docs = scan(_es, index=esconfig.ES_INPUT_INDEX,
                doc_type=esconfig.ES_INPUT_DOCTYPE,
                query=query, size=(limit or 1000), fields="")
    for i, a in enumerate(docs):
        if limit and i >= limit:
            return
        yield a['_id']

    
def get_cached_documents(ids, doc_type):
    res = _es.mget(index=esconfig.ES_RESULT_INDEX,
                   doc_type=doc_type, body={"ids": ids})
    for doc in res['docs']:
        if doc['found']:
            d = Document(doc['_id'], doc['_source']['pipeline'], doc['_source']['result'], doc_type)
            yield d.id, d
    
def get_document(id, doc_type):
    res= _es.get(index=esconfig.ES_RESULT_INDEX,
                 doc_type=doc_type, id=id)
    return Document(id, res['_source']['pipeline'], res['_source']['result'], doc_type)

def store_result(doc_type, id, pipeline, result):
    _check_mapping(doc_type)
    if isinstance(result, bytes):
        # elastic wants 'text', not 'bytes'
        result = result.decode("utf-8")
    body = dict(id=id, pipeline=pipeline, result=result)
    _es.index(index=esconfig.ES_RESULT_INDEX,
              doc_type=doc_type,
              body = body,
              id = id)

def exists(doc_type, id):
    return _es.exists(index=esconfig.ES_RESULT_INDEX, doc_type=doc_type, id=id)

def delete_result(doc_type, id):
    _es.delete(index=esconfig.ES_RESULT_INDEX, doc_type=doc_type, id=id)
    

def _split_list(items, batch_size=1000):
    return (items[i:i+batch_size] for i in range(0, len(items), batch_size))
    
def _count_cached(ids):
    body = {'query': {u'filtered': {u'filter': {'ids': {u'values': ids}}}},
            'aggregations': {u'aggregation': {u'terms': {u'field': u'_type'}}}}
    res = _es.search(index=esconfig.ES_RESULT_INDEX, body=body, size=0)
    for bucket in res['aggregations']['aggregation']['buckets']:
        yield bucket['key'], bucket['doc_count']
    
def count_cached(ids):
    result = {}
    for batch in _split_list(ids):
        for key, n in _count_cached(batch):
            result[key] = result.get(key, 0) + n
    return result.items()


    
def _get_cached_document_ids(ids, doc_type):
    res = _es.mget(index=esconfig.ES_RESULT_INDEX,
                   doc_type=doc_type, body={"ids": ids}, _source=False)
    for doc in res['docs']:
        if doc['found']:
            yield doc['_id']

def get_cached_document_ids(ids, doc_type):
    """Get the ids of documents that have been parsed with this doc_type"""
    for batch in _split_list(ids):
        for id in _get_cached_document_ids(batch, doc_type):
            yield id
