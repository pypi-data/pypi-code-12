
from rdflib import Graph, URIRef
from rdflib.namespace import Namespace
from StringIO import StringIO

SCM = Namespace('http://www.smartdeveloperhub.org/vocabulary/scm#')

g = Graph()

g.bind('scm', SCM)

with open('branch.ttl') as ttl:
    g.parse(StringIO(ttl.read()), format='turtle')

commits = list(g.objects(URIRef('http://russell.dia.fi.upm.es/scmharvester/repositories/42/branches/3/'), SCM.hasCommit))
for c in commits:
    print c
