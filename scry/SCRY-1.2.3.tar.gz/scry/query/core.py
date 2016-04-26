import re
import pyparsing as pp
import rdflib.plugins.sparql as sparql

from rdflib.graph import Graph, ConjunctiveGraph
from rdflib.term  import URIRef, Variable
from tempfile     import mkdtemp
from shutil       import rmtree

from scry.query.contexts import OrbHandler, ProcedureHandler, VarProcedureHandler, ValuesHandler, BindHandler
from scry.query.patch    import ServiceHandler
from scry.utility        import SCRY, SCRYError



class QueryHandler(object):
    
    def __init__(self, query, procedures, orb_description, user_environment):
        
        # Initialization attributes
        self.query_string = query                             # The raw, unparsed query string
        self.query        = sparql.prepareQuery(query)        # An object with .prologue and .algebra attributes, generated from a query string through RDFLib's SPARQL parser
        self.procedures   = procedures                        # The loaded procedure dictionary, pointing from PAUs to procedures
        self.orb_desc     = orb_description                   # An RDF graph describing these procedures in further detail
        self.user_env     = user_environment                  # A dictionary for procedures to store/share whatever data they require
        
        # Execution attributes
        self.query_type       = None                          # One of: 'SELECT', 'CONSTRUCT', 'ASK' or 'DESCRIBE'
        self.triples          = list()                        # A list of triples parsed from the query algebra
        self.prefixes         = str()                         # Prefix statements parsed from the front of a query string
        self.service_clauses  = list()                        # A list of federated subqueries, marked by SERVICE <endpoint> {} clauses
        self.service_handlers = list()                        # A list of service handlers -- subset of context_handlers
        self.response_type    = None                          # The selected MIME type of the response
        self.graph            = ConjunctiveGraph()            # The graph object against which 'query' will be resolved
        self.orb_description  = False                         # When an OrbHandler adds the scry:orb_description context, this attribute stores the pointer to it
        self.context_handlers = list()                        # A list of context handlers, needed for the bookkeeping of call_procedures()
        self.var_binders      = dict()                        # A dictionary of ?variables used in the query, pointing to the context_handlers that bind values to them        
        self.result           = None                          # An RDFLib Result object, generated through graph.query() at the end of resolve()
        self.temp_dirs        = list()                        # A list of temporary directories generated for this query's service calls
                                                              # Automatically cleaned up after resolving, even in case of errors

        #from rdflib.plugins.sparql.algebra import pprintAlgebra
        #print 'ALGEBRA'
        #pprintAlgebra(self.query)
        
        # Share the service_handlers list through the query object's prologue:
        self.query.prologue.service_handlers = self.service_handlers

        # Include the orb_description graph by default:
        g  = Graph(self.graph.store,SCRY.orb_description)
        g += self.orb_desc

    

    def resolve(self):
        # Invoke, in order, the following methods:
        #
        #   parse_query()
        #   call_procedures()
        #   graph.query()
        #   cleanup()
        #
        # Finally, return the bound result set


        try:
            self.parse_query()        # Parse the triples and possibly a VALUES statement from the query -- sets the 'query', 'query_type', 'triples', 'values' and 'values_vars' attributes
            self.call_procedures()    # Populate the 'graph' attribute's RDF graph by invoking the procedures encoded in 'triples'
            self.eval_query()         # Evaluate 'query' against 'graph'                                 -- sets the 'result' attribute
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
                elif n == 'ServiceGraphPattern':
                    if not self.service_clauses:
                        parse_service_clauses(self.query_string)
                    h = ServiceHandler(self,algebra,self.service_clauses.pop(0))
                    self.context_handlers.append(h)
                    self.service_handlers.append(h)
                    return
                for key in algebra:
                    if key == 'triples':
                        for t in algebra[key]:
                            self.triples.append(t)
                    parse_algebra(algebra[key])
        
        def parse_service_clauses(qry): # CAUTION: This breaks if there's curly closing brackets } in Literals (or URIs)...
            service_pattern      = pp.CaselessLiteral('SERVICE') + pp.Word(pp.printables) + pp.nestedExpr('{','}')
            self.service_clauses = [re.sub(r'\s+',' ',qry[p[1]:p[2]]) for p in service_pattern.scanString(qry)]
            prefix_pattern       = pp.CaselessLiteral('PREFIX') + pp.Word(pp.alphanums) + pp.Literal(':') + pp.nestedExpr('<','>')
            self.prefixes        = '\n'.join([qry[p[1]:p[2]] for p in prefix_pattern.scanString(qry)])
        
        parse_algebra(self.query.algebra)


    def call_procedures(self):
        # First,  determine which triples use SCRY predicates (input, output, OTHERS???) and assign them to the appropriate ProcedureHandlers
        # Second, determine I/O dependence between the ContextHandlers
        # Third,  execute context handlers in the appropriate order, passing on outputs as inputs where required
        
        call_dict     = dict() # A dictionary mapping Procedure Associated URIs to their call handlers
        var_call_dict = dict() # Similar to ^, except mapping Variable URIs to their call handlers
        def get_call_handler(uri):
            if uri in call_dict:
                return call_dict[uri]
            
            if isinstance(uri,URIRef):
                short_uri = URIRef(uri.encode().split('?')[0]) # Crop off parameters if any are specified
                if short_uri in self.procedures:
                    proc = self.procedures[short_uri]
                    handler        = ProcedureHandler(self,proc,uri)
                    call_dict[uri] = handler
                    self.context_handlers.append(handler)
                else:
                    raise SCRYError("A SCRY predicate was used with a subject URI that is not associated with any procedures: %s" % uri.encode())
                return call_dict[uri]
            elif isinstance(uri,Variable):
                if uri not in var_call_dict:
                    handler = VarProcedureHandler(self,uri)
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
                for v in h.output_vars:
                    if v not in output_dict:
                        output_dict[v] = set()
                    output_dict[v].add(h)
            
            output_vars = output_dict.keys()
            for s in self.service_handlers:
                s.set_bound_vars(output_vars or True)
                for v in s.output_vars:
                    if v not in output_dict:
                        output_dict[v] = set()
                    output_dict[v].add(s)
            
            for h in self.context_handlers:
                for v in h.input_vars:
                    try:
                        h.dependencies = h.dependencies.union(output_dict[v])
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


    def eval_query(self):
        
        self.result = self.graph.query(self.query)
        

    def get_temp_dir(self):
        path = mkdtemp()
        self.temp_dirs.append(path)
        return path


    def cleanup(self):
        for path in self.temp_dirs:
            rmtree(path)
            
### END OF QueryHandler