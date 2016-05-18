"""
Base classes for NLPipe tasks
"""


from __future__ import absolute_import

import datetime

from .celery import app
from .backend import get_document, get_input, store_result, exists
import logging
import time
import subprocess
class NLPipeModule(app.Task):
    """
    Preprocessing module that handles the elastic interface
    Implementing tasks should return the processed string.
    Class variables version, input_doc_type, output_doc_type, doc can be used to set options.
    If doc is True, the nlpipe.document will be passed to the task rather than the raw text.

    Example usage:
    @app.Task(base=NLPipeModule, version=1.0)
    def test_task(text):
        return text.upper()
    """
    abstract = True
    version = "0.0"
    input_doc_type = None # defaults to text (raw) input
    output_doc_type = None # defaults to name__version
    doc =False # if true, pass document rather than just input
    
    def __init__(self, *args, **kwargs):
        super(NLPipeModule, self).__init__(*args, **kwargs)
        self.process = self.run
        self.run = self.run_wrapper

    @property
    def doc_type(self):
        if self.output_doc_type:
            return self.output_doc_type
        return "{name}__{version}".format(name=self.name.split(".")[-1], version=self.version.replace(".", "_"))

    def run_wrapper(self, id, check_exists=True):
        self.id = id
        if check_exists and exists(self.doc_type, id):
            return
        if self.input_doc_type is None:
            # task is bsed on raw input
            doc = get_input(id)
        else:
            doc = get_document(id, self.input_doc_type)
        begin_time = datetime.datetime.now()
        t = time.time()
        logging.info("({self.name}) Processing {id}".format(**locals()))
        result = self._process(doc if self.doc else doc.text)
        end_time = datetime.datetime.now()

        provenance  = dict(module=self.name, version=self.version,
                           input_type=doc.input_type, input_fields=doc.input_fields,
                           begin_time=begin_time, end_time=end_time)
        
        logging.info("({self.name}) Storing {id} ({time:.2f}s)".format(time=time.time()-t, **locals()))
        store_result(self.doc_type, id, doc.pipeline + [provenance], result)
        logging.info("({self.name}) Finished {id} ({time:.2f}s)".format(time=time.time()-t, **locals()))

    def _process(self, text):
        return self.process(text)
        
    def get_result(self, id):
        return get_document(id, self.doc_type)
        
        
class NLPSystemModule(NLPipeModule):
    """
    NLP Module that uses a system (shell) call

    Tasks should define the cmd property, i.e. @task(... ,cmd="shell command")
    Tasks will be called with the result, and may return a postprocessed text.
    If tasks return None, the result of the system call will be stored
    """
    abstract = True
    cmd = None
    def _process(self, text):
        if self.cmd is None:
            raise ValueError("NLPSystemModule task requires cmd to be set")
        p2 = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        (out, err) = p2.communicate(text.encode("utf-8"))
        if p2.returncode != 0:
            raise Exception("Error on calling shell command: {self.cmd} (see logs)".format(**locals()))
        out = out.decode("utf-8")
        postprocessed = self.process(out)
        return out if postprocessed is None else postprocessed

    
