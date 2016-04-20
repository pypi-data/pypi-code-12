from rdflib              import Namespace
from rdflib.term         import URIRef

SCRY = Namespace('http://www.scry.rocks/')
A    = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')


def make_bool(s):
    if s.lower() in ['1','y','yes','t','true']:
        return True
    return False
    

class SCRYError(Exception):       pass
class URIError(SCRYError):        pass
class EmptyListError(ValueError): pass