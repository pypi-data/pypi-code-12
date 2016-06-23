from pyesgf.search import SearchConnection
import cf
import json
#david@ilex>> chmod 600 ~/.esg/credentials.pem
#david@ilex>> myproxyclient logon  -s myproxy.ceda.ac.uk -b -C ~/.esg/certificates -o ~/.esg/credentials.pem -l davidhassell
#Enter password for user 'davidhassell' on MyProxy server 'myproxy.ceda.ac.uk':
#david@ilex>> pwd
#/home/david/cf-python
#david@ilex>> ipython

# http://home.badc.rl.ac.uk/mjuckes/esgfNcview/
# http://ndg-security.ceda.ac.uk/wiki/Howtos/ESGFDownloadScript
# http://ndg-security.ceda.ac.uk/wiki/MyProxyClient
# http://pythonhosted.org/cdb_query/recipes.html
institute = 'MOHC'
model = 'HadGEM2-ES'
experiment = 'rcp45'

_connection = SearchConnection('http://pcmdi9.llnl.gov/esg-search', distrib=True)

class ESGF(object):
    
    def __init__(self):
        self._context = {}

    def context():       
        return self._context.copy()

    def search(**kwargs):    
        self._context = kwargs
        self.ctx = _connection.new_context(**kwargs)
    
    def constrain(**kwargs):    
        self._context.update(kwargs)
        self._ctx = self._ctx.constrain(**kwargs)
    
    def opendap_urls():    
        self._context.update(kwargs)
        self._ctx = self._ctx.constrain(**kwargs)
    
        result = self._ctx.search()[0]
        agg_ctx = result.aggregation_context()
        agg = agg_ctx.search()

        urls = []
        for a in agg:
            url = a.opendap_url
            if url is None:
                continue
            
            ursl.append(url)
        #--- End: for
    #--- End: def

    def facate_counts(**kwargs):
    
        ctx = _connection.new_context(**kwargs)
    
        print 'ctx.hit_count=',ctx.hit_count

data_nodes = ctx.get_facet_options()['data_node']

while data_nodes:

    data_node = data_nodes.popitem()[0]
    print 'data_node:',data_node

    ctx2 = ctx.constrain(data_node=data_node)

    print 'ctx2.hit_count=',ctx2.hit_count
    if ctx2.hit_count != 1:
        print 'BAD HIT COUNT'
        break

    result = ctx2.search()[0]
    agg_ctx = result.aggregation_context()
    agg = agg_ctx.search()

#    if len(agg) == 0:
#        continue
    
    print 'lll', len(agg)

    f = None
    for a in agg:
        url = a.opendap_url
        if url is None:
            continue

        if '.r1i1p1.psl.' in url:
            print url
            try:
                f = cf.read(url)
            except RuntimeError:
                pass

            break
    #--- End: for

    if f is not None:
#        print f
        break
#--- End: while
           
serial_file = institute+'_'+model+'_'+experiment+'_esgf.json'

d = {'serial_file' : serial_file,
     'opendap_url' : url,
 }

if f is not None:


    ctx_rips = conn.new_context(project='CMIP5',
                                institute=institute,
                                model=model,
                                experiment=experiment)
    rips = sorted(ctx_rips.facet_counts['ensemble'].keys())
    try:              
        rips.remove('r0i0p0')            
    except ValueError:                
        pass
    print str(len(rips)),'ensemble members: ', ', '.join(rips)+')'
    d['ensembleMembers'] = str(len(rips))
    d['drsMember'] =  ', '.join(rips)

    for prop in ['parent_experiment_rip',
                 'experiment_id',
                 'experiment',
                 'institute_id',
                 'parent_experiment_id',
                 'model_id',
                 ]:
        d[prop] = sorted(set(f.getprop(prop, None)))
        if prop != 'parent_experim
