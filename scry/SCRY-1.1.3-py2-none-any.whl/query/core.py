import rdflib.plugins.sparql as sparql

from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.term  import URIRef, Variable
from tempfile     import mkdtemp
from shutil       import rmtree

from scry.query.contexts import OrbHandler, ServiceHandler, VarServiceHandler, ValuesHandler, BindHandler
from scry.utility        import SCRY, SCRYError



class QueryHandler(object):
    
    def __init__(self, query, procedures, orb_description, user_environment):
        
        # Initialization attributes
        self.query      = sparql.prepareQuery(query)          # An object with .prologue and .algebra attributes, generated from a query string through RDFLib's SPARQL parser
        self.procedures = procedures                          # The loaded procedure dictionary, pointing from PAUs to procedures
        self.orb_desc   = orb_description                     # An RDF graph describing these procedures in further detail
        self.user_env   = user_environment                    # A dictionary for procedures to store/share whatever data they require
        
        # Execution attributes
        self.query_type       = None                          # One of: 'SELECT', 'CONSTRUCT', 'ASK' or 'DESCRIBE'
        self.triples          = list()                        # A list of triples parsed from the query algebra
        self.response_type    = None                          # The selected MIME type of the response
        self.graph            = ConjunctiveGraph()            # The graph object against which 'query' will be resolved
        self.orb_description  = False                         # When an OrbHandler adds the scry:orb_description context, this attribute stores the pointer to it
        self.context_handlers = list()                        # A list of context handlers, needed for the bookkeeping of call_services()
        self.var_binders      = dict()                        # A dictionary of ?variables used in the query, pointing to the context_handlers that bind values to them        
        self.result           = None                          # An RDFLib Result object, generated through graph.query() at the end of resolve()
        self.temp_dirs        = list()                        # A list of temporary directories generated for this query's service calls
                                                              # Automatically cleaned up after resolving, even in case of errors

        g  = Graph(self.graph.store,SCRY.orb_description)
        g += self.orb_desc

    

    def resolve(self):
        # Invoke, in order, the following methods:
        #
        #   parse_query()
        #   call_services()
        #   graph.query()
        #   cleanup()
        #
        # Finally, return the bound result set


        try:
            self.parse_query()                         # Parse the triples and possibly a VALUES statement from the query -- sets the 'query', 'query_type', 'triples', 'values' and 'values_vars' attributes
            self.call_services()                       # Populate the 'graph' attribute's RDF graph by invoking the procedures encoded in 'triples'
            self.result = self.graph.query(self.query) # Evaluate 'query' against 'graph'                                 -- sets the 'result' attribute
            self.cleanup()
            return self.result

        except SCRYError as e:
            self.output = e.description
            self.cleanup()
            raise e


    def parse_query(self):
        self.query_type = self.query.algebra.name[0:-5].upper() # 'SELECT', 'CONSTRUCT', 'ASK' or 'DESCRIBE'

        def parse_algebra(algebra):
            if isinstance(algebra,sparql.algebra.CompValue):
                n = algebra.name
                if n == 'values':
                    self.context_handlers.append(ValuesHandler(self,algebra))
                elif n == 'Extend':
                    self.context_handlers.append(BindHandler(self,algebra))
                elif n == 'Graph' and algebra.term == SCRY.orb_description:
                    self.context_handlers.append(OrbHandler(self,algebra))
                    return
                for key in algebra:
                    if key == 'triples':
                        for t in algebra[key]:
                            self.triples.append(t)
                    parse_algebra(algebra[key])
        parse_algebra(self.query.algebra)


    def call_services(self):
        # First,  determine which triples use SCRY predicates (input, output, OTHERS???) and assign them to the appropriate ServiceHandlers
        # Second, determine I/O dependence between the ServiceHandlers
        # Third,  call the services in the appropriate order, passing on outputs as inputs where required
        #         [Refine this to also take specifications from VALUES and BIND statements into account!]
        #         [Fake it with ServiceHandler subclasses?]
        
        call_dict     = dict() # A dictionary mapping Procedure Associated URIs to their call handlers
        var_call_dict = dict() # Similar to ^, except mapping Variable URIs to their call handlers
        def get_call_handler(uri):
            if uri in call_dict:
                return call_dict[uri]
            
            if isinstance(uri,URIRef):
                short_uri = URIRef(uri.encode().split('?')[0]) # Crop off parameters if any are specified
                if short_uri in self.procedures:
                    proc = self.procedures[short_uri]
                    handler        = ServiceHandler(self,proc,uri)
                    call_dict[uri] = handler
                    self.context_handlers.append(handler)
                else:
                    raise SCRYError("A SCRY predicate was used with a subject URI that is not associated with any procedures: %s" % uri.encode())
                return call_dict[uri]
            elif isinstance(uri,Variable):
                if uri not in var_call_dict:
                    handler = VarServiceHandler(self,uri)
                    var_call_dict[uri] = handler
                    self.context_handlers.append(handler)
                return var_call_dict[uri]
        
        def parse_triples():
            for t in self.triples:
                if t[0] == SCRY.orb:
#                   self.describe_orb()
                    continue
                pred = URIRef(t[1].encode().split('?')[0]) # Strip any specifiers/parameters from the predicate
                if pred == SCRY.input:
                    get_call_handler(t[0]).add_input(t)
                elif pred == SCRY.output:
                    get_call_handler(t[0]).add_output(t)
                elif pred in [SCRY.author, SCRY.description, SCRY.provenance, SCRY.version]:
                    get_call_handler(t[0]).add_description(t)
        
        output_dict = dict() # A dictionary mapping bound variables to the execution handlers that bind them as outputs
        def set_dependencies():
            for h in self.context_handlers:
                h.set_bound_vars()
                for output in h.output_vars:
                    if output not in output_dict:
                        output_dict[output] = set()
                    output_dict[output].add(h)
            
            for h in self.context_handlers:
                for var in h.input_vars:
                    try:
                        h.dependencies = h.dependencies.union(output_dict[var])
                    except KeyError as k:
                        raise SCRYError("Unable to resolve depencies involving the Variable %s" % k)

        def execute_all():
            for h in self.context_handlers:
                while not h.executed:
                    indep = h.get_independent_handler(list())
                    indep.execute()
                        
        parse_triples()
        set_dependencies()
        execute_all()


    def get_temp_dir(self):
        path = mkdtemp()
        self.temp_dirs.append(path)
        return path


    def cleanup(self):
        for path in self.temp_dirs:
            rmtree(path)
            
### END OF QueryHandler