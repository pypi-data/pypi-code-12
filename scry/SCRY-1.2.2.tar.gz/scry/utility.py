from werkzeug.exceptions import HTTPException
from rdflib              import Namespace
from rdflib.term         import URIRef

SCRY = Namespace('http://scry.rocks/')
A    = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')


def make_bool(s):
    if s.lower() in ['1','y','yes','t','true']:
        return True
    return False
    

class SCRYError(HTTPException):
    def __init__(self, desc, code=500):
        Exception.__init__(self)
        self.description = "\n\nSCRY error: %s\n\n" % desc
        self.code        = code
        print self.description
        
class URIError(SCRYError):        pass
class EmptyListError(ValueError): pass