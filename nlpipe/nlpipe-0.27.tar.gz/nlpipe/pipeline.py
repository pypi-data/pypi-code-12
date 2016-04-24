from .backend import get_document, get_cached_documents, get_cached_document_ids
from elasticsearch.exceptions import NotFoundError
from random import sample
import logging

def get_result(id, task):
    try:
        return task.get_result(id)
    except NotFoundError:
        t = task.delay(id)
        t.wait()
        return task.get_result(id)
        

def get_results(ids, task, only_cached=False):
    docs = dict(get_cached_documents(ids, task.doc_type))
    if not only_cached:
        for id in ids:
            if id not in docs:
                docs[id] = get_result(id, task)
    return docs

def parse_background(ids, task, max=None, queue='background'):
    parsed = set(get_cached_document_ids(ids, task.doc_type))
    todo = list(set(ids) - set(parsed))
    toparse = todo
    if (max is not None) and (max < len(todo)):
        toparse = sample(toparse, max)
    logging.info("{nparsed}/{n} articles already parsed, assigning {ntoparse} out of {ntodo}"
          .format(n=len(ids), nparsed=len(parsed), ntoparse=len(toparse), ntodo=len(todo)))

    for i, id in enumerate(toparse):
        if i >0 and not (i % 1000):
            logging.info("... Assigning {i}".format(**locals()))
        task.apply_async(args=[id], queue=queue)
