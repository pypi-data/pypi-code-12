import os
import imp
import pkg_resources as pkr

from rdflib.graph import Graph
from rdflib.term  import Literal

from scry.config           import get_conf, get_subdir
from scry.utility          import SCRY, URIError
from scry.services.classes import Service, Procedure

# SCRY loads its services from a configurable directory. Every module*
# accessible from that directory will be imported. Then:
#
# 1) If an instance of the Service class can be retrieved via
#    getattr(mod,'DESCRIPTION'), SCRY uses that object to determine which
#    Procedures and URIs it should load.
#
# 2) Else, if there is one, SCRY will use the first (and only the first)
#    instance of the Service class it encounters while looping through dir(mod).
#
# 3) Else, if it exists, SCRY will load every instance of the Procedure class in
#    the '__all__' list.
#
# 4) Else, SCRY will load every instance of the Procedure class it encounters
#    while looping through dir(mod).
#
# *: A "module" here means any file with the .py extension, and any subdirectory
#    containing an __init__.py file. Other files and directories without an init
#    file are ignored.
#
# The result of this process is a dictionary which has procedure-associated URIs
# (PAUs) as keys, pointing to the corresponding Procedure class instances.
#
# Note that the directory should also contain a (hidden) file called '.scry'.
# This ini-formatted file has two multiline fields: no-load and remote-load. Any
# module whose name matches one of the lines in no-load will not be loaded.
# Conversely, SCRY will try to import every line in remote-load even if no such
# module is present in the directory.



def load():
    
    S    = dict()
    P    = dict()

    def load_module(mod):
        name = mod.__name__
        if hasattr(mod,'DESCRIPTION') and isinstance(mod.DESCRIPTION,Service):
            S[name] = mod.DESCRIPTION               # Scenario (1)
        else:
            attlist = list()
            for att in dir(mod):
                v = getattr(mod,att)
                if isinstance(v,Service):
                    S[name] = v                     # Scenario (2)
                elif isinstance(v,Procedure):
                    attlist.append(att)             # Narrow down list for scenario (4)
            if hasattr(mod,'__all__'):              # Scenario (3)
                attlist = mod.__all__
            if name not in S:
                S[name] = Service()
                for att in attlist:
                    v = getattr(mod,att)
                    if isinstance(v,Procedure):
                        S[name].add_procedure(v)
            return S[name].get_procedures()

    def merge(d1,d2):        # Using this function instead of dictionaries' update method to track overlapping PAUs.
        s1 = set(d1)
        s2 = set(d2)
        if s1.intersection(s2):
            raise URIError("More than one procedure is registered to the URI <%s>" % s1.intersection(s2).pop())
        d1.update(d2)

    directory  = get_subdir('Services')
    ll, rl, nl = find_services(directory)

    for m in ll:
        mod = imp.load_source(m,ll[m])
        merge(P,load_module(mod))
    for m in rl:
        if m:
            mod = __import__(m)
            merge(P,load_module(mod))
            
    return S, P



def find_services(directory):

    ld          = os.listdir(directory)
    conf        = get_conf()
    local_load  = dict()
    remote_load = [mod.strip() for mod in conf.get('Services','remote-load').strip().split('\n')]
    no_load     = [mod.strip() for mod in conf.get('Services','no-load').strip().split('\n')]

    while '' in remote_load: remote_load.remove('')
    while '' in no_load: no_load.remove('')

    for f in ld:
        m = False
        if f.endswith('.py'):
            m = f[:-3]
            p = os.path.join(directory,f)
        else:
            path = os.path.join(directory,f)
            init = os.path.join(path,'__init__.py')
            if os.path.isdir(path) and os.path.isfile(init):
                m = f
                p = init
        if m and m not in no_load:
            local_load[m] = p

    return local_load, remote_load, no_load



def describe(d):
    g    = Graph()
    
    version = pkr.get_distribution('scry').version
    g.add((SCRY.orb, SCRY.author, Literal('Bas Stringer')))
    g.add((SCRY.orb, SCRY.description, Literal('SCRY - the SPARQL Compatible seRvice laYer (version %s)' % version)))
    g.add((SCRY.orb, SCRY.version, Literal(version)))
        
    for uri in d:
        proc = d[uri]
        desc = proc.get_description()
        g   += desc

    return g