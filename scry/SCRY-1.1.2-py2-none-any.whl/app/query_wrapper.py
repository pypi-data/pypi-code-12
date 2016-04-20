# A QueryWrapper is instantiated every time Flask receives a request on the
# .../scry/ route. It preprocesses the HTTP request so that a query string may
# be passed to the core program's QueryHandler, and will convert results to an
# accepted format to provide an appropriate response.

from flask        import Response
from scry.app     import SUPPORTED_REQUEST_METHODS, SUPPORTED_RESPONSE_TYPES, DEFAULT_RESPONSE_TYPE
from scry.app.log import log_request, log_response
from scry.query   import QueryHandler
from scry.utility import SCRYError



class QueryWrapper(object):
    
    def __init__(self,request,g):
        self.request         = request              # The HTTP request object as passed by Flask
        self.global_dict     = g                    # The global environment dictionary of the Flask application
        self.parsed          = dict()               # A dictionary for the results of parsing the HTTP request
        self.response_type   = None                 # The MIME type selected for the response
        self.handler         = None                 # A pointer to the QueryHandler object instantiated for this request
        self.result          = None                 # A pointer to the QueryHandler's result set produced during run_query()
        self.output          = None                 # Formatted results, generated through result.serialize()
    
    
    def resolve(self):
        # Invoke, in order, the following methods:
        #
        #   parse_http()
        #   select_response_type()
        #   run_query()
        #   format_results()
        #   cleanup()
        #
        # Finally, return the appropriate flask.Response

        try:
            date, time = log_request(self.request)
            self.parse_http()           # Retrieve required information from the HTTP request              -- sets the 'parsed' attribute
            self.select_response_type() # Based on ^, determine how to serialize the results later on      -- executed here to assert a valid response type is supported
            self.run_query()            # Instantiate and resolve a QueryHandler object                    -- sets the 'handler' and 'result' attributes
            self.format_result()        # Serialize the results in a way determined by 'response_type'     -- sets the 'output' attribute
            self.cleanup()
            log_response(self.output, date, time)

            return Response(self.output, mimetype=self.response_type)            

        except SCRYError as e:
            self.output = e.description
            self.cleanup()
            log_response(self.output, date, time)
            raise e


    def parse_http(self):
        # Parse the HTTP request for relevant headers, the request method, and the query string.
        rq     = self.request
        parsed = dict()        

        def parse_http_request_method():
            if rq.method == 'GET':
                method = 'get'
            else: # POST
                content_type = rq._parsed_content_type[0]
                if content_type == 'application/sparql-query':
                    method = 'direct-post'
                elif content_type == 'application/x-www-form-urlencoded':
                    method = 'url-encoded-post'
                else:
                    raise AttributeError('Invalid SPARQL request')
            if method not in SUPPORTED_REQUEST_METHODS:
                raise NotImplementedError('Handling %s SPARQL requests has not yet been implemented.' % method)
            return method

        def parse_http_query_parameters():
            ### NEEDS REFINEMENT AND MORE THOROUGH TESTING WITH DIFFERENT TYPES OF QUERIES AND TRIPLE STORES
            ### NOT SURE IF request.values['query'] ALWAYS EXISTS, OR WHERE TO GRAB DEFAULT AND NAMED GRAPHS FROM
            query_string  = rq.values['query']
            default_graph = ''
            named_graphs  = []
            return query_string, default_graph, named_graphs    
        
        method                       = parse_http_request_method()
        parsed['method']             = method

        accepted                     = str(rq.accept_mimetypes).split(',')
        parsed['accepted_responses'] = [a.split(';')[0] for a in accepted] # Ignore parameters (like q [preference], level, etc.)
        
        q_string, q_default, q_named = parse_http_query_parameters()
        parsed['query_string']       = q_string
        parsed['default_graph']      = q_default
        parsed['named_graphs']       = q_named

        self.parsed = parsed
    
    
    def select_response_type(self):
        # Based on the parsed information and implementation status quo, select an appropriate MIME type for the HTTP response.
        
        ### NEEDS REFINEMENT AND MORE THOROUGH TESTING WITH DIFFERENT TYPES OF QUERIES
        ### HAVE TO CHECK IF ALL RESPONSE TYPES ARE VALID FOR ALL QUERY TYPES, AND IF NOT, MAKE SEPARATE LISTS FOR SELECT/CONSTRUCT/ASK
        accepted = self.parsed['accepted_responses']
        default  = DEFAULT_RESPONSE_TYPE
        if default in accepted:
            self.response_type = default
        else:
            for t in SUPPORTED_RESPONSE_TYPES:
                if t in accepted:
                    self.response_type = t.strip()
                    break
            
            if self.response_type is None:
                if '*/*' in accepted:
                    self.response_type = default
                else:
                    raise NotImplementedError(("None of the request's accepted response types are currently implemented.\n" +
                                               "Implemented : %s\n" % ', '.join(SUPPORTED_RESPONSE_TYPES.keys())         +
                                               "Accepted    : %s\n" % ', '.join(accepted)))


    def run_query(self):
        # Instantiate a handler; resolve the query; retrieve results.
        g = self.global_dict
        g[self] = dict()
        self.handler = QueryHandler(self.parsed['query_string'],g['procedures'],g['orb_description'],g[self])
        self.result  = self.handler.resolve()


    def format_result(self):
        if self.response_type is not None:
            format = SUPPORTED_RESPONSE_TYPES[self.response_type]
        else:
            format = 'xml'  
        self.output = self.result.serialize(format = format)
 
       
    def cleanup(self):
        if self.handler: del self.handler
        if self in self.global_dict: del self.global_dict[self]