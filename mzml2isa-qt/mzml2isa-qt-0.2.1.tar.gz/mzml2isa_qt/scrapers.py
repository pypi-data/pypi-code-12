## BACKEND
import sys
import os
import json
import urllib.error
import urllib.request as rq
from urllib.parse import quote

## FRONTEND
from PyQt5.QtCore import QThread, pyqtSignal



class SparOntologyThread(QThread):

    Finished = pyqtSignal('QString')

    def __init__(self):
        super(SparOntologyThread, self).__init__()

    def run(self):
        try:
            onto = json.loads(rq.urlopen(self.jsonSourceUrl).read().decode('utf-8'))
            info = []
            for x in onto:
                if '@type' in x:
                    if self.ontoClass in x['@type']:
                        info.append(x)
            info = [ (x['http://www.w3.org/2000/01/rdf-schema#label'],x['@id']) for x in info ]
            info = json.dumps({x[0]['@value'].capitalize():y for (x,y) in info})
        except: #urllib.error.URLError:
            with open(os.path.join(os.path.dirname(__file__), os.path.join("ontologies", self.sparName + os.path.extsep + 'json')), 'r') as f:
                info = f.read()
        finally:
            self.Finished.emit(info)


class PSOThread(SparOntologyThread):
    """A thread to scrape the Publishing Status Ontology"""

    def __init__(self):
        super(PSOThread, self).__init__()
        self.jsonSourceUrl = "http://www.sparontologies.net/ontologies/pso/source.json"
        self.sparName = "pso"
        self.ontoClass = "http://purl.org/spar/pso/PublicationStatus"


class PROThread(SparOntologyThread):
    """A thread to scrape the Publishing Roles Ontology"""
    def __init__(self):
        super(PROThread, self).__init__()
        self.jsonSourceUrl = "http://www.sparontologies.net/ontologies/pro/source.json"
        self.sparName = "pro"
        self.ontoClass = "http://purl.org/spar/pro/PublishingRole"



class OlsSearcher(QThread):
    """A thread that searches the Ontology Lookup Service."""

    Finished = pyqtSignal('QString')

    def __init__(self, query, rows=200):
        super(OlsSearcher, self).__init__()
        self.searchUrl = "http://www.ebi.ac.uk/ols/api/search/?q={}"\
            "&groupField=1&rows={}".format(query, rows)

    def run(self):
        try:
            request = rq.FancyURLopener({})
            with request.open(self.searchUrl) as url_opener:
                result = json.loads(url_opener.read().decode('utf-8'))
            
                if not 'response' in result or result['response']['numFound'] == 0:
                    answer = ('')
                else:
                    answer = json.dumps(result['response']['docs'])
                    
        except:
            answer = ''
        finally:
            self.Finished.emit(answer)


class OlsExplorer(QThread):
    """A thread that get the informations of a class based on its iri."""
  
    Finished = pyqtSignal('QString', 'QString')

    def __init__(self, short_ref, prefix, iri, ):
        super(OlsExplorer, self).__init__()
        self.ref = short_ref
        self.url = 'http://www.ebi.ac.uk/ols/api/ontologies/{prefix}' \
                    '/terms/{iri}'.format(prefix=prefix, 
                                          iri=quote(quote(iri, safe=''), safe='')
                                          )


    def run(self):
        try:
            request = rq.FancyURLopener({})
            with request.open(self.url) as url_opener:
                self.result = url_opener.read().decode('utf-8')
        except urllib.error:
            self.result = ''
        finally:
            self.Finished.emit(self.ref, self.result)


class OlsOntologist(QThread):
    """A thread that get the informations of an ontology based on its prefix."""
   
    Finished = pyqtSignal('QString', 'QString')

    def __init__(self, prefix, parent=None, *args, **kwargs):
        super(OlsOntologist, self).__init__(parent, *args, **kwargs)
        self.prefix = prefix
        self.url = 'http://www.ebi.ac.uk/ols/api/ontologies/{prefix}'.format(prefix=prefix) 


    def run(self):
        try:
            request = rq.FancyURLopener({})
            with request.open(self.url) as url_opener:
                result = json.loads(url_opener.read().decode('utf-8'))
                self.config = result['config']
        except urllib.error:
            self.result = ''
        finally:
            self.Finished.emit(self.prefix, json.dumps(self.config))


