from bottle import route, static_file
import os.path

corpus_path = None

def init(path):
    global corpus_path
    corpus_path = path

@route('/fulltext/<doc_id>')
def get_doc(doc_id):
    return static_file(doc_id, root=corpus_path)

import os.path
def label(doc):
    path = os.path.join(corpus_path, doc)
    if os.path.exists(path):
        with open(path) as docfile:
            docfile = docfile.read()
            return doc + ': ' + ' '.join(docfile.split()[:10]) + ' ...'
    else:
        return doc
