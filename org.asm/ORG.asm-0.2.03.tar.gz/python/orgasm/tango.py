"""
.. module:: orgasm.tango
   :platform: Unix
   :synopsis: The :py:mod:`~orgasm.tango` package contains a set of functions useful to manage assembling structure.

The :py:mod:`orgasm.tango` package
==================================

The :py:mod:`~orgasm.tango` package contains a set of functions useful to manage assembling structure.

.. moduleauthor:: Eric Coissac <eric.coissac@inria.fr>

:author:  Eric Coissac
:contact: eric.coissac@inria.fr


.. warning::

    The :py:mod:`~orgasm.tango` package functions aims to be integrated 
    into other packages as standalone functions of class methods.
"""
import sys
from orgasm.multialign import multiAlignReads, consensus  # @UnresolvedImport
from orgasm.assembler import Assembler                    # @UnresolvedImport
from orgasm.assembler import buildstem                    # @UnresolvedImport
from orgasm.assembler import tango                        # @UnresolvedImport
from orgasm.utils import tags2str

from time import time
import math
from functools import reduce


def cutLowCoverage(self,mincov,terminal=True):
    '''
    Remove sequences in the assembling graph with a coverage below ``mincov``.
    
    .. code-block :: ipython
    
        In [159]: asm = Assembler(r)

        In [160]: s = matchtoseed(m,r)

        In [161]: a = tango(asm,s,mincov=1,minread=10,minoverlap=30,maxjump=0,cycle=1)
    
        In [162]: asm.cleanDeadBranches(maxlength=10)

        Remaining edges : 424216 node : 423896
        Out[162]: 34821
        In [162]: cutLowCoverage(asm,10,terminal=False)

    :param mincov: coverage threshold 
    :type mincov: :py:class:`int`
    :param terminal: if set to ``True`` only terminal edges are removed from the assembling graph
    :type terminal: :py:class:`bool`
    :return: the count of deleted node
    :rtype: :py:class:`int`
    
    :seealso: :py:meth:`~orgasm.assambler.Assembler.cleanDeadBranches`
    '''    
    def isTerminal(g,n):
        return len(list(g.parentIterator(n)))==0 or len(list(g.neighbourIterator(n)))==0
    
    def endnodeset(g):
        return set(g.nodeIterator(predicate = lambda n : (len(list(g.neighbourIterator(n)))==0)))
    
    def startnodeset(g):
        return set(g.nodeIterator(predicate = lambda n : (len(list(g.parentIterator(n)))==0)))
    
    
    if terminal:
        tstates=[True]
    else:
        tstates=[True,False]
    ilength=len(self)
    cg = self.compactAssembling(verbose=False)
    
    index = self.index
    readSize = index.getReadSize()
    for terminal in tstates:
        print('',file=sys.stderr)
        if terminal:
            print("Deleting terminal branches",file=sys.stderr)
        else:
            print("Deleting internal branches",file=sys.stderr)
        extremities = endnodeset(cg) | startnodeset(cg)
        go = True
        while go:
            go = False
            stems = [x for x in cg.edgeIterator() 
                     if not terminal or (isTerminal(cg, x[0]) or isTerminal(cg, x[1]))]
            if stems:
                stems.sort(key=lambda i:cg.getEdgeAttr(*i)['weight'],reverse=True)
                lightest = stems.pop()
                lattr = cg.getEdgeAttr(*lightest)
#                 print >>sys.stderr
#                 print >>sys.stderr,lattr['stemid'],len(stems),lightest[0],lightest[1],lattr['weight']
        #         print >>sys.stderr,lattr['weight'] < mincov
        #         print >>sys.stderr,isTerminal(cg, lightest[0]), isTerminal(cg, lightest[1])
        #         print >>sys.stderr,lattr['weight'] < mincov and ((not terminal) or isTerminal(cg, lightest[0]) or isTerminal(cg, lightest[1]))
        #         print >>sys.stderr
                if lattr['weight'] < mincov: 
                    if stems:
                        go=True
                    for n in lattr['path'][1:-1]:
                        if n in self.graph:
                            try:
                                del self.graph[n]
                            except KeyError:
                                pass
                    if lightest[0] in extremities and lightest[0] in self.graph:
                        del self.graph[lightest[0]]
                    if lightest[1] in extremities and lightest[1] in self.graph:
                        del self.graph[lightest[1]]
                        
                    print("Remaining edges : %d node : %d\r" % (self.graph.edgeCount(),len(self)),
                          end='\r',
                          file=sys.stderr)
        
                    cg.deleteEdge(*lightest)
                    tojoin=[]
                    if lightest[0] in extremities:
                        del cg[lightest[0]]
                    else:
                        tojoin.append(lightest[0])
                    if lightest[1] in extremities:
                        del cg[lightest[1]]
                    else:
                        tojoin.append(lightest[1])
#                    print >>sys.stderr,lightest[0] in extremities,lightest[1] in extremities,tojoin
                    for c in tojoin:
                        if c in cg:
                            begin = list(cg.parentIterator(c))
                            end   = list(cg.neighbourIterator(c))
                            if len(begin)==1 and len(end)==1:
                                begin = begin[0]
                                end = end[0]
                                e1s = list(cg.edgeIterator(edgePredicate = lambda e:e[0]==begin and e[1]==c))
                                e2s = list(cg.edgeIterator(edgePredicate = lambda e:e[0]==c and e[1]==end))
                                if len(e1s)==1 and len(e2s)==1:
                                    e1 = e1s[0]
                                    e2 = e2s[0]
                                    attr1 = cg.getEdgeAttr(*e1)
                                    attr2 = cg.getEdgeAttr(*e2)

                                    sequence=attr1['sequence'] + attr2['sequence']
                                    path=attr1['path'] + attr2['path'][1:]
                                    
                                    stem =  buildstem(self,
                                                      begin,
                                                      end,
                                                      sequence,
                                                      path,
                                                      False)
                                    
                                    stem['graphics']={'width':int(stem['weight']/readSize)+1,
                                                      'arrow':'last'}
                                    
                                    cg.addStem(stem)
    
                                    cg.deleteEdge(*e2)                                        
                                    cg.deleteEdge(*e1)  
                                    
                                    
                                    del cg[c]                  
                                
    print('',file=sys.stderr)
    return ilength - len(self)

def cutSNPs(self,maxlength=500):
    cg = self.compactAssembling(verbose=False)
    snps = [(snp, 
             1 if snp[2][0][1][2] > snp[2][1][1][2] else 0)   # indicate which allele needs to be elimimated
             for snp in [(i,                                  # start node
                         next(cg.neighbourIterator(i)),      # end node
                         [(k[2],                              # allele id (0 or 1) 
                           (cg.getEdgeAttr(*k)['stemid'],     # allele stemid
                            cg.getEdgeAttr(*k)['length'],     # allele length
                            cg.getEdgeAttr(*k)['weight'])     # allele coverage
                           ) 
                          for k in cg.edgeIterator(edgePredicate=lambda j:j[0]==i)
                         ]
                        ) 
                        for i in cg.nodeIterator(predicate=lambda n : 
                                len(list(cg.neighbourIterator(n))) == 1 
                                and len(list(cg.edgeIterator(edgePredicate=lambda e : e[0]==n)))==2)
                      ] if  snp[2][0][1][0]>0                 # keep one copy of the snp
                        and snp[2][0][1][0]!=-snp[2][1][1][0] # exclude pairs of reverse-complement allele
                        and snp[2][0][1][1]<maxlength               # exclude allele longer than 500 bp 
                        and snp[2][1][1][1]<maxlength             #
           ]
           
    for snp in snps:
        edge  = cg.getEdgeAttr(snp[0][0],snp[0][1],snp[1])
        nodes = edge['path'][1:-1]
        print("Remaining edges : %d node : %d" % (self.graph.edgeCount(),len(self)),
              end='\r',
              file=sys.stderr)
        for node in nodes:
            if node in self.graph:
                del self.graph[node]
    print("",file=sys.stderr)
    
  
def mode(data):
    '''
    Compute a raw estimation of the mode of a data set
    
    :param data: The data set to analyse
    :type data: a permanent iterable object (list, tuble...)
    
    '''

    data = list(data)
    
    if len(data) == 0:
        return None
    
    if len(data) < 8:
        return int(sum(data)/len(data))
    
    data.sort()
    xx = [0,0,0]
    for j in range(3):
        windows = len(data)//2
        intervals = [data[i+windows]-data[i] for i in range(windows)]
        mininter = min(intervals)
        begininter = intervals.index(mininter)
        data = data[begininter:(begininter+windows)]
        xx[j]=sum(data)/windows

    return sum(xx)/3

def weightedMode(data):
    d = []
    for x,w in data:
        d.extend([x] * w)
    return mode(d)   
    
def matchtoseed(matches,index,new=None):
    s=[]
    if new is None:
        new=list(matches.keys())
        
    for p in new:
        m = matches[p][1]
        k = m.keys()
        for x in k:
            s.extend((index.getIds(y[0])[0],(x,),0) for y in m[x])  

    return s

def matchtogene(matches):
    genes = {}
    if matches is not None:
        for p in matches:        # Loop over probe set
            m = matches[p][1]
            k = m.keys()
            for x in k:          # Loop over a probes in a set
                for i in m[x]:   # loop over matches in a probe
                    if i[0] < 0:
                        pos = -i[5]
                    else:
                        pos = i[5]
                    genes[abs(i[0])]=(x,pos)
            
    return genes

def genesincontig(cg,index,matches):
    def vread(i):
        if abs(i) > len(index):
            v=0
        elif abs(i) in genes:
            v=1
        else:
            v=-1
        return v
    
    genes = matchtogene(matches)
    ei = cg.edgeIterator(edgePredicate=lambda e: 'path' in cg.getEdgeAttr(*e))
    
    for e in ei:
        ea = cg.getEdgeAttr(*e)
        path = ea['path']
        eg = [vread(i) for i in path]
        ep = [genes.get(abs(i),()) for i in path]
            
        g = sum(i for i in eg if i > 0)
        if g > 0:
            g=max(min(math.ceil(math.log10(g)),4)*64-1,0)
            color="#00%02X%02X" % (g,255-g)
        else:
            color="#0000FF"
        graphics = ea.get('graphics',{})
        graphics['arrow']='last'
        graphics['fill']=color
        ea['graphics']=graphics
        ea['ingene']=g
        ea['genepos']=ep
          
    

def scaffold(self,assgraph,minlink=5,back=200,addConnectedLink=False):
    '''
    Add relationships between edges of the assembling graph related to the
    par ended links.
    
    :param assgraph: The compact assembling graph as produced by the
                     :py:meth:`~orgasm.assembler.Assembler.compactAssembling` method
    :type assgraph:  :py:class:`~orgasm.graph.DiGraphMultiEdge`
    :param minlink:  the minimum count of pair ended link to consider 
                     for asserting the relationship
    :type minlink:   :py:class:`int`
    :param back:     How many base pairs must be considered at the end of each edge
    :type back:      :py:class:`int`
    :param addConnectedLink: add to the assembling graph green edges for each directly 
                             connected edge pair representing the pair ended links 
                             asserting the connection.
    :type addConnectedLink: :py:class:`bool`
     '''
    
    if addConnectedLink:
        # Fake function just testing the stemid attribute
        def isInitial(n):
            return  'stemid' in assgraph.getEdgeAttr(*n) 
        def isTerminal(n):
            return  'stemid' in assgraph.getEdgeAttr(*n) 
    else:
        def isInitial(n):
            return len(list(assgraph.parentIterator(n[0],edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))))==0 
        def isTerminal(n):
            return len(list(assgraph.neighbourIterator(n[1],edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))))==0

        
    ei = [i for i in assgraph.edgeIterator(edgePredicate=isInitial)]
    et = [i for i in assgraph.edgeIterator(edgePredicate=isTerminal)]
    
    eiid = [assgraph.getEdgeAttr(*i)['stemid'] for i in ei]
    etid = [assgraph.getEdgeAttr(*i)['stemid'] for i in et]
    
    nei = len(ei)
    net = len(et)

    s=[]
    for e1 in range(net):
        for e2 in range(nei):
            connected = et[e1][1]==ei[e2][0]
            linkedby,ml,sl  = pairEndedConnected(self,assgraph,etid[e1],eiid[e2],back)

            if connected and addConnectedLink:
                if linkedby >= minlink:
                    s.append((et[e1][1],ei[e2][0],linkedby,etid[e1], eiid[e2],"#00FF00"))
                    print("%d -> %d connection asserted by %d pair ended links" % (etid[e1], eiid[e2],linkedby),
                          file=sys.stderr)
                else:
                    print("%d -> %d connection not asserted by pair ended link" % (etid[e1], eiid[e2]),
                          file=sys.stderr)
            if not connected and linkedby >= minlink:
                s.append((et[e1][1],ei[e2][0],linkedby,etid[e1], eiid[e2],"#FF0000"))
                print("%d -> %d scaffolded by %d pair ended links" % (etid[e1], eiid[e2],linkedby),
                      file=sys.stderr)
                
    for x,y,z,s1,s2,color in s:
        attr = assgraph.addEdge(x,y)
        attr['label']="Gap (%d)  %d -> %d" % (z,s1,s2)
        attr['graphics']={'width':z // 10.,
                          'arrow':'last',
                          'fill':color
                          }
__cacheAli = set()
__cacheAli2 = set()

def fillGaps(self,minlink=5,
                  back=200,
                  kmer=12,
                  smin=40,
                  delta=0,
                  cmincov=5,
                  minread=20,
                  minratio=0.1, 
                  emincov=1,
                  maxlength=None,
                  gmincov=1,
                  minoverlap=60,
                  lowfilter=True,
                  adapters5=(),
                  adapters3=(),
                  maxjump=0,
                  snp=False,
                  nodeLimit=1000000,
                  onlyLinking=False,
                  logger=None):
    '''
    
    :param minlink:
    :param back:
    :param kmer:
    :param smin:
    :param delta:
    :param cmincov:
    :param minread:
    :param minratio:
    :param emincov:
    :param maxlength:
    :param gmincov:
    :param minoverlap:
    :param lowfilter:
    :param maxjump:
    :param snp: If set to True (default value is False) erase SNP variation
                by conserving the most abundant version
    '''
    global __cacheAli
    global __cacheAli2
    __cacheAli = __cacheAli2
    __cacheAli2 = set()
    
    def isInitial(n):
        return len(list(assgraph.parentIterator(n[0],edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))))==0 
    def isTerminal(n):
        return len(list(assgraph.neighbourIterator(n[1],edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))))==0

    assgraph = self.compactAssembling(verbose=False)
    
    index = self.index
    
    ei = [i for i in assgraph.edgeIterator(edgePredicate=isInitial)]
    et = [i for i in assgraph.edgeIterator(edgePredicate=isTerminal)]
    
    eiid = [assgraph.getEdgeAttr(*i)['stemid'] for i in ei]
    etid = [assgraph.getEdgeAttr(*i)['stemid'] for i in et]

    epi = [set(assgraph.getEdgeAttr(*i)['path'][0:back]) for i in ei]
    ept = [set(assgraph.getEdgeAttr(*i)['path'][-back:]) for i in et]

    eei = [set(assgraph.getEdgeAttr(*i)['path'][0:100]) for i in ei]
    eet = [set(assgraph.getEdgeAttr(*i)['path'][-100:]) for i in et]
    print(eiid) # <EC>
    exi = [getPairedRead(self,assgraph,i,back,end=False) for i in eiid]
    ext = [getPairedRead(self,assgraph,i,back,end=True) for i in etid]
    
    nei = len(ei)
    net = len(et)
    s=[]
    maxcycle=max(self.graph.getNodeAttr(i)['cycle'] for i in self.graph)
    lassemb = len(self)
    cycle = maxcycle
    linked=set()
    extended=set()
    for e1 in range(net):
        for e2 in range(nei):
            connected = et[e1][1]==ei[e2][0]
            if not connected:
                linkedby,ml,sl  = pairEndedConnected(self,assgraph,etid[e1],eiid[e2],back)
            
                if linkedby >= minlink and abs(etid[e1]) <= abs(eiid[e2]):
                    extended.add(etid[e1])
                    extended.add(-eiid[e2])
                    if (etid[e1],eiid[e2]) not in linked:
                        linked.add((-eiid[e2],-etid[e1]))
                        print("\n\nLinking Stems %d -> %d" % (etid[e1],eiid[e2]),
                              file=sys.stderr)

                        ex = frozenset(((ext[e1] | exi[e2]) - ept[e1] - epi[e2]) | eet[e1] | eei[e2])
                        
                        ingraph = sum(i in self.graph for i in ex)
                        nreads = len(ex)
                        if ingraph < nreads:
                            print ("--> %d | %d = %d reads to align (%d already assembled)" % (len(ext[e1]),len(exi[e2]),nreads,ingraph),
                                  file=sys.stderr)

                            if nreads > 10:
                                __cacheAli2.add(ex)
                                if ex not in __cacheAli:
                                    ali= multiAlignReads(ex,index,kmer,smin,delta)
                                    print('',file=sys.stderr)
                
                                    #goodali = [i for i in ali if len(i) >= nreads/4]
                                    goodali=ali
                                    print("--> %d consensus to add" % len(goodali),
                                          file=sys.stderr)

                                    for a in goodali:
                                        cycle+=1
                                        c = consensus(a,index,cmincov)
                                        s = insertFragment(self,c,cycle=cycle)
                                        print("     %d bp (%d reads) added on cycle %d" % (len(c),len(s),cycle),
                                              file=sys.stderr)

            
                                        a = tango(self,
                                                  seeds      = s,
                                                  minread    = minread,
                                                  minratio   = minratio,
                                                  mincov     = emincov,
                                                  minoverlap = minoverlap,
                                                  lowfilter  = lowfilter,
                                                  adapters5   = adapters5,
                                                  adapters3   = adapters3,
                                                  maxjump    = maxjump,
                                                  cycle      = cycle,
                                                  nodeLimit  = nodeLimit)
                                        
                                        
                                        print('',file=sys.stderr)
                                else:
                                    print("--> already aligned",file=sys.stderr)

    if not onlyLinking:
        for e1 in range(net):
            if etid[e1] not in extended:
                print("\n\nExtending Stems %d" % (etid[e1]),
                      file=sys.stderr)
    
                ex = frozenset((ext[e1] - ept[e1]) | eet[e1])
                nreads = len(ex)
                print("--> %d reads to align" % (nreads),
                      file=sys.stderr)
    
                if nreads > 10:
                    __cacheAli2.add(ex)
                    if ex not in __cacheAli:
                        ali= multiAlignReads(ex,index,kmer,smin,delta)
                        print('',file=sys.stderr)
                        #goodali = [i for i in ali if len(i) >= nreads/4]
                        goodali=ali
                        print("--> %d consensus to add" % len(goodali),
                              file=sys.stderr)
    
                        for a in goodali:
                            c = consensus(a,index,cmincov)
                            if c:
                                cycle+=1
                                s = insertFragment(self,c,cycle=cycle)
                                print("     %d bp (%d reads) added on cycle %d" % (len(c),len(s),cycle),
                                      file=sys.stderr)
    
                                a = tango(self,
                                          seeds      = s,
                                          minread    = minread,
                                          minratio   = minratio,
                                          mincov     = emincov,
                                          minoverlap = minoverlap,
                                          lowfilter  = lowfilter,
                                          adapters5  = adapters5,
                                          adapters3  = adapters3,
                                          maxjump    = maxjump,
                                          cycle      = cycle,
                                          nodeLimit  = nodeLimit)
                            print("",file=sys.stderr)
                    else:
                        print("--> already aligned",file=sys.stderr)

    self.cleanDeadBranches(maxlength=10)
    cutLowCoverage(self,gmincov,terminal=True)
#    cutLowCoverage(self,int(gmincov/3),terminal=False)   
    
    if maxlength is not None:
        smallbranches = maxlength
    else:
        smallbranches = estimateDeadBrancheLength(self)
        print("     Dead branch length setup to : %d bp" % smallbranches,
              file=sys.stderr)

    self.cleanDeadBranches(maxlength=smallbranches)

    if snp:
        cutSNPs(self)

    newnodes = len(self) - lassemb
    
    print('',file=sys.stderr)
    print("#######################################################",file=sys.stderr)
    print("#",file=sys.stderr)
    print("# Added : %d bp (total=%d bp)" % (newnodes/2,len(self)/2),file=sys.stderr)
    print("#",file=sys.stderr)
    print("#######################################################",file=sys.stderr)
    print('',file=sys.stderr)
    
    return newnodes

                        
                        


        
def insertFragment(self,seq,cycle=1):
    index = self.index
    rsize = index.getReadSize()
    readmax=len(index)+1
    seeds = set()
    ireadidE=None
    
    if len(seq) >= rsize:
        graph = self.graph
        probe = seq[0:rsize]
        readid = index.getReadIds(probe)
        
        for i in range(1,len(seq)-rsize+1):
            coverage = readid[1]
            ireadid   = readid[0]
            seeds.add(ireadid)
            
            if ireadid not in graph:
                node  = graph.addNode(ireadid)
                if 'cycle' not in node:
                    node['cycle']=cycle
                if ireadid < readmax:
                    node['fake5']=0
                    node['fake3']=0
                else:
                    node['graphics']={'fill':"#0000FF"}
                
            probe = seq[i:i+rsize]
            readidE = index.getReadIds(probe)
            coverage = readidE[1]
            ireadidE   = readidE[0]
            
            if ireadidE not in graph:
                node  = graph.addNode(ireadidE)
                if 'cycle' not in node:
                    node['cycle']=cycle
                if ireadidE < readmax:
                    node['fake5']=0
                    node['fake3']=0
                else:
                    node['graphics']={'fill':"#0000FF"}
                    
            
            #if ireadid!=-ireadidE:
            edges = graph.addEdge(ireadid,ireadidE)
            edges[1]['coverage']=coverage
            edges[2]['coverage']=coverage
            edges[1]['label']="%s (%d)" % (edges[1]['ext'],coverage)
            edges[2]['label']="%s (%d)" % (edges[2]['ext'],coverage)
            #else:
            #    print >>sys.stderr,"\nWARNING : self loop on %d" % ireadidE
        
            readid = readidE
        
        if ireadidE is not None:    
            seeds.add(ireadidE)
        
    return [(-abs(i),("Consensus",),0) for i in seeds]
                

def getPairedRead(self,assgraph,stemid,back,end=True): 
    '''
    
    :param assgraph:
    :type assgraph:
    :param stemid:
    :type stemid:
    :param back:
    :type back:
    :param end:
    :type end:
    '''
    r = self.index 
    lr = len(r)
    
    if not end:
        stemid=-stemid  
    
    stem = next(assgraph.edgeIterator(edgePredicate=lambda e:'stemid' in assgraph.getEdgeAttr(*e) 
                                                 and assgraph.getEdgeAttr(*e)['stemid']==stemid))
                                                 
    path=assgraph.getEdgeAttr(*stem)['path'][-back:]
    
    reads=[set(r.normalizedPairedEndsReads(abs(i))[1]) for i in path if  abs(i) < lr]
    paired = set(reduce(lambda a,b: a | b,reads,set()))
    
    if not end:
        paired = set(-i for i in paired)
    
    return paired

def pairEndedConnected(self,assgraph,edge1,edge2,back=250):
    '''
    Returns how many pair ended reads link two edges in a compact assembling graph
    
    :param assgraph: The compact assembling graph as produced by the
                     :py:meth:`~orgasm.assembler.Assembler.compactAssembling` method
    :type assgraph:  :py:class:`~orgasm.graph.DiGraphMultiEdge`
    :param edge1:    The ``stemid`` of the first edge
    :type edge1:     :py:class:`int`
    :param edge2:    The ``stemid`` of the second edge
    :type edge2:     :py:class:`int`
    :param back:     How many base pairs must be considered at the end of each edge
    :type back:      :py:class:`int`
    
    :return:         The count of pair ended reads linking both the edges
    :rtype:          :py:class:`int`
    '''
    
    ri = self.index
    lri= len(ri)
        
    s1 = next(assgraph.edgeIterator(edgePredicate=lambda e:'stemid' in assgraph.getEdgeAttr(*e) 
                                                 and assgraph.getEdgeAttr(*e)['stemid']==edge1))
                                                 
    s2 = next(assgraph.edgeIterator(edgePredicate=lambda e:'stemid' in assgraph.getEdgeAttr(*e) 
                                                 and assgraph.getEdgeAttr(*e)['stemid']==edge2))
                                                 
    e1 = assgraph.getEdgeAttr(*s1)['path'][-back:]
    e2 = assgraph.getEdgeAttr(*s2)['path'][0:back]

    de1 = {}
    de2 = {}
    j   = 0
    for i in e1:
        l = de1.get(i,[])
        de1[i] = l
        l.append(j)
        j+=1

    j   = 0
    for i in e2:
        l = de2.get(i,[])
        de2[i] = l
        l.append(j)
        j+=1
        

    pe1 = [k for k in 
           [(a,[j for j in b if j in de2]) 
            for a,b in [ri.normalizedPairedEndsReads(i) 
                        for i in e1 if i > 0 and i < lri]] if k[1]]
    
    pe2 = [k for k in 
           [(a,[j for j in b if j in de1]) 
            for a,b in [ri.normalizedPairedEndsReads(i) 
                        for i in e2 if i < 0 and -i < lri]] if k[1]]
    le1=len(e1)
    peset = set()
    delta = []
    for f,rs in pe1:
        for r in rs:
            p = (f,abs(r)) if f < abs(r) else (abs(r),-f)
            if p not in peset:
                peset.add(p)
                for p1 in de1[f]:
                    for p2 in de2[r]:
                        delta.append(le1 - p1 + 1 + p2)
 
    pe2set = set()
    
    for f,rs in pe2:
        for r in rs:
            p = (-f,abs(r)) if -f < abs(r) else (abs(r),f)
            if p not in peset:
                peset.add(p)
                for p1 in de1[r]:
                    for p2 in de2[f]:
                        delta.append(le1 - p1 + 1 + p2)
 
    if (len(delta)):
        dmean = sum(delta) / len(delta)
        dmean2= sum(x ** 2 for x in delta)  / len(delta)        
        dsd   = math.sqrt(dmean2 - dmean ** 2)
        dmean+=ri.getReadSize()
    else:
        dmean = None
        dsd  = None
        
    return len(peset),dmean,dsd
    
def coverageEstimate(self,matches=None,index=None,timeout=60.0):
    '''
    Estimates the average coverage depth of the sequence.
    
    The algorithm is masic and can be very slow. To avoid infinity
    computation time a timeout limits it to 60 secondes by default.
    
    Three values are returned by the function :
    
        - The number of bp considered to estimate the coverage
        - The length of the segment used for the estimation
        - The coverage depth 
        
    
    
    
    :param timeout: Maximum computation time.
    
    :return: a triplet (int,int,float) 
    '''
    def weight(a,b):
        maxw=0
        for e in cg.edgeIterator(edgePredicate = lambda i:i[0]==a and i[1]==b):
            attr = cg.getEdgeAttr(*e)
            w = attr['length'] * attr['weight']
            if w > maxw:
                maxw=w        
        return maxw 
    
    def coverage(start):
        wp = cg.minpath(start, distance=weight,allowCycle=True)
#        print ">>>",start,wp
        maxpath = max(wp[0].values())
        maxend=[i for i in wp[0] if wp[0][i]==maxpath][0]
        i=maxend
        path=[i]
        if i == start and wp[0][i] > 0:
            i=wp[1][i]
            path.append(i)
        while i!=start:
            i=wp[1][i]
            path.append(i)
        return(maxpath,path)
    
    cg = self.compactAssembling(verbose=False)
        
    if matches is not None and index is not None:
        genesincontig(cg, index, matches)
        # A first and fast approach is to look for long sequence (> 1kb)
        
        longweight = [(cg.getEdgeAttr(*i)['weight'],cg.getEdgeAttr(*i)['length'])
                        for i in cg.edgeIterator(edgePredicate=lambda e:'weight' in cg.getEdgeAttr(*e)) 
                        if cg.getEdgeAttr(*i)['length'] > 1000 and cg.getEdgeAttr(*i)['ingene']>0]
    else:
        # A first and fast approach is to look for long sequence (> 1kb)
        
        longweight = [(cg.getEdgeAttr(*i)['weight'],cg.getEdgeAttr(*i)['length'])
                        for i in cg.edgeIterator(edgePredicate=lambda e:'weight' in cg.getEdgeAttr(*e)) 
                        if cg.getEdgeAttr(*i)['length'] > 1000]
                    
    if longweight:
        maxpath = sum(i[1] for i in longweight)
        cov = weightedMode((i[0],i[1]//100) for i in longweight)
        return maxpath,maxpath,cov
    
    # Seconde strategy : we look for the longest of the shortest path
    
    maxpath=0
    path=None
    btime = time()
    n=list(cg)
    # n = [i  for i in cg if len(list(cg.parentIterator(i)))==0]
    # dest = [i  for i in cg if len(list(cg.neighbourIterator(i)))==0]
    e = [max([cg.getEdgeAttr(*j)['length'] 
              for j in list(cg.edgeIterator(edgePredicate=lambda i: i[1]==k))]+[0]) 
         for k in n]
    ne = list(map(lambda a,b:(a,b),n,e))
    ne.sort(key=lambda i:i[1],reverse=True)
    n = [i[0] for i in ne]
    
    for i in n:
        w,p = coverage(i)
        if w > maxpath:
            maxpath=w
            path=p
        if (time()-btime) > timeout:
            break 
#    print path        

    if path:
        path.reverse()
        j = path[0]
        cumlength=0
        for i in path[1:]:
            maxw=0
            maxlength=0
            for e in cg.edgeIterator(edgePredicate = lambda k:k[0]==j and k[1]==i):
                attr = cg.getEdgeAttr(*e)
                w = attr['length'] * attr['weight']
#                print w , attr['length'] , attr['weight']
                if w > maxw:
                    maxw=w
                    maxlength=attr['length']       

            cumlength+=maxlength
            j=i
    else:
        l = [(cg.getEdgeAttr(*e)['length']) 
                for e in cg.edgeIterator(edgePredicate=lambda e: 'stemid' in cg.getEdgeAttr(*e))]
        w = [(cg.getEdgeAttr(*e)['weight']) 
                for e in cg.edgeIterator(edgePredicate=lambda e: 'stemid' in cg.getEdgeAttr(*e))]
        if l:
            maxpath=max(l)
            coverage = w[l.index(maxpath)]
            return maxpath,maxpath,coverage
        else:
            return None,None,None        # <-- ???
    return maxpath,cumlength,maxpath/float(cumlength)


def path2fasta(self,assgraph,path,identifier="contig",minlink=10,nlength=20,back=200,logger=None,tags=[]):
    '''
    Convert a path in an compact assembling graph in a fasta formated sequences.
    
    :param assgraph: The compact assembling graph as produced by the
                     :py:meth:`~orgasm.assembler.Assembler.compactAssembling` method
    :type assgraph:  :py:class:`~orgasm.graph.DiGraphMultiEdge`
    :param path:     an ``iterable`` providing an ordered list of ``stemid`` indicating
                     the path to follow.  
    :type path:      an ``iterable`` over :py:class:`int`
    :param identifier: the identifier used in the header of the fasta formated sequence
    :type identifier:  :py:class:`bytes`
    :param minlink:  the minimum count of pair ended link to consider 
                     for asserting the relationship
    :type minlink:   :py:class:`int`
    :param nlength:  how many ``N`` must be added between two segment of sequences only connected
                     by pair ended links
    :type nlength:   :py:class:`int`
    :param back:     How many base pairs must be considered at the end of each edge
    :type back:      :py:class:`int`
    
    :returns: a string containing the fasta formated sequence
    :rtype: :py:class:`bytes`

    :raises: :py:class:`AssertionError`
    '''
    frglen,frglensd = estimateFragmentLength(self)
    
    alledges = dict((assgraph.getEdgeAttr(*e)['stemid'],e) 
                    for e in assgraph.edgeIterator(edgePredicate = lambda i: 'stemid' in assgraph.getEdgeAttr(*i)))

    
#     def getEdge(stemid):
#         stem = assgraph.edgeIterator(edgePredicate=lambda e:'stemid' in assgraph.getEdgeAttr(*e) 
#                                                        and  assgraph.getEdgeAttr(*e)['stemid']==stemid).next()
#         return stem
        
    #print alledges
        
    coverage=[]
    slength=[]
    seq=[]
    label=[]
    oldstem=None
    oldid=None
    
    
    
    rank = 1
    forceconnection=False

    for stemid in path:
        if stemid != 0:
            stem = alledges[stemid]
            attr = assgraph.getEdgeAttr(*stem)
            
            #print "@@>",stemid,attr['length'],stem,oldstem
    
            if oldstem is not None:
                connected,ml,sl = pairEndedConnected(self,assgraph,oldid,stemid,back)
                if oldstem[1]==stem[0]:
                    if ml is not None:
                        if logger is None:
                            print("Both segments %d and %d are connected (paired-end=%d frg length=%f sd=%f)" % (oldid,stemid,connected,float(ml),float(sl)),
                                  file=sys.stderr)
                        else: 
                            logger.info("Both segments %d and %d are connected (paired-end=%d frg length=%f sd=%f)" % (oldid,stemid,connected,float(ml),float(sl)))
    
                        label.append('{connection: %d - length: %d, sd: %d}' % (connected,int(ml),int(sl)))
                    else:
                        if logger is None:
                            print("Both segments %d and %d are connected but covered by 0 paired-end" % (oldid,stemid),
                                  file=sys.stderr)
                        else: 
                            logger.info("Both segments %d and %d are connected but covered by 0 paired-end" % (oldid,stemid))
    
                        label.append('{connection: 0}')
                        
                else:
                    if logger is None:
                        print("Both segments %d and %d are disconnected" % (oldid,stemid),
                              file=sys.stderr)
                    else: 
                        logger.info("Both segments %d and %d are disconnected" % (oldid,stemid))
                    if connected >= minlink:
                        glength = frglen - ml - self.index.getReadSize() 
                        
                        if logger is None:
                            print("   But linked by %d pair ended links (gap length=%f sd=%f)" % (connected,float(glength),float(sl)),
                                  file=sys.stderr)
                        else:
                            logger.info("   But linked by %d pair ended links (gap length=%f sd=%f)" % (connected,float(glength),float(sl)))
                        if glength > 0:
                            seq.append(b'N'*int(glength))
                            slength.append(int(glength))
                        else:
                            seq.append(b'N'*3)

                        seq.append(self.index.getRead(stem[0],0,self.index.getReadSize()).lower())
                        slength.append(self.index.getReadSize())
                        label.append('{N-connection: %d - Gap length: %d, sd: %d}' % (connected,int(glength),int(sl)))
                    elif forceconnection:
                        if connected > 0:
                            
                            glength = int(frglen-ml - self.index.getReadSize()) 

                            if logger is None:
                                print("Connection is forced with only %d pair ended links (gap length=%f sd=%f)" % (connected,float(glength),float(sl)),
                                      file=sys.stderr)
                            else:
                                logger.info("Connection is forced with only %d pair ended links (gap length=%f sd=%f)" % (connected,float(glength),float(sl)))
                                
                        else:
                            
                            if logger is None:
                                print("Connection is forced without pair ended links",
                                      file=sys.stderr)
                            else:
                                logger.info("Connection is forced without pair ended links")
                                
                            glength =  nlength
                        
                        seq.append(b'N'*int(glength))
                        seq.append(self.index.getRead(stem[0],0,self.index.getReadSize()).lower())
                        slength.append(self.index.getReadSize())
                        
                        if connected > 0:
                            label.append('{F-connection: %d - Gap length: %d, sd: %d}' % (connected,int(glength),int(sl)))
                        else:
                            label.append('{F-connection: %d}' % connected)
                            
                        flink = assgraph.addEdge(oldstem[1],stem[0])
                        rlink = assgraph.addEdge(-stem[0],-oldstem[1])
                        flink['label']="Forced (%d)  %d -> %d" % (connected,oldid,stemid)
                        flink['graphics']={'width':1,
                                           'arrow':'last',
                                           'fill':'pink'
                                          }
                        rlink['label']="Forced (%d)  %d -> %d" % (connected,-stemid,-oldid)
                        rlink['graphics']={'width':1,
                                           'arrow':'last',
                                           'fill':'pink'
                                          }
                    else:
                        raise AssertionError('Disconnected path between stem '
                                             '%d and %d only %d pair ended links' % (oldid,stemid,connected))
            
            allsteps = attr.get('steps',{})
            steps = allsteps.get(identifier,[])
            steps.append(rank)
            allsteps[identifier]=steps
            attr['steps']=allsteps
            
            rank+=1
    
            
            seq.append(attr['sequence'])
            coverage.append(attr['weight'])
            slength.append(attr['length'])
            label.append(attr['label'])
            
            oldstem = stem
            oldid=stemid
            
            forceconnection=False
        else:
            forceconnection=True
        
    s1 = alledges[path[-1]]
    s2 = alledges[path[0]]
    sid1=assgraph.getEdgeAttr(*s1)['stemid']
    sid2=assgraph.getEdgeAttr(*s2)['stemid']
    connected,ml,sl = pairEndedConnected(self,assgraph,sid1,sid2,back)
    
    if s1[1]==s2[0]:
        
        if logger is None:
            print("Path is circular",file=sys.stderr)
        else:
            logger.info("Path is circular")
            
        circular=True
        label.append('{connection: %d}' % connected)
    else:
        if connected >= minlink:
            glength = frglen - ml - self.index.getReadSize() 

            if logger is None:
                print("Path is circular but disconnected" ,file=sys.stderr)
                print("  But linked by %d pair ended links  (gap length=%f sd=%f)" % (connected,float(glength),float(sl)),file=sys.stderr)
            else:
                logger.info("Path is circular but disconnected")
                logger.info("Linked by %d pair ended links  (gap length=%f sd=%f)" % (connected,float(glength),float(sl)))
                
            label.append('{N-connection: %d}' % connected)
            seq.append(b'N'* int(glength))
            slength.append(int(glength))
            circular=True
        elif forceconnection:
            if logger is None:
                print("Circular connection forced",file=sys.stderr)
                print("Linked by %d pair ended links" % connected,file=sys.stderr)
            else:
                logger.info("Circular connection forced")
                logger.info("Linked by %d pair ended links" % connected)
                
            label.append('{F-connection: %d}' % connected)
            seq.append(b'N'*int(nlength))
            circular=True
        else:
            if logger is None:
                print("Path is linear",file=sys.stderr)
            else:
                logger.info("Path is linear")
            circular=False
        seq.insert(0,self.index.getRead(s2[0],0,self.index.getReadSize()).lower())
        slength.insert(0,self.index.getReadSize())

    for stemid in set(path):
        if stemid !=0:
            stem = alledges[stemid]
            attr = assgraph.getEdgeAttr(*stem)
            
            sequence = attr['sequence']
            graphics = attr.get('graphics',{})
            graphics['style']='dashed'
            attr['graphics']=graphics
            
            
            if attr['length'] > 10:
                attr['label']="%d : %s->(%d)->%s  [%d] @ %s" % (stemid,sequence[0:5].decode('ascii'),
                                                                attr['length'],
                                                                sequence[-5:].decode('ascii'),
                                                                int(attr['weight']),
                                                                attr['steps'])
            else:
                attr['label']="%d : %s->(%d)  [%d] @ %s" % (stemid,
                                                            sequence.decode('ascii'),
                                                            attr['length'],
                                                            int(attr['weight']),
                                                            attr['steps'])
    
    sequence = b''.join(seq)
    length = sum(slength)
    mcov = sum(a * b for a,b in map(lambda a,b:(a,b),slength,coverage)) / float(length)
    
    fasta=[">%s seq_length=%d; coverage=%5.1f; circular=%s; %s%s" % (identifier,length,
                                                                  mcov,circular,
                                                                  tags2str(tags) + " ",
                                                                  '.'.join(label))]
    fasta.extend(sequence[i:i+60].decode('ascii') for i in range(0,len(sequence),60))
    return "\n".join(fasta)
    

def pathConstraints(self,cg,threshold=5.,back=500, minlink=5):

    def minisatDoubleConstraints(self,cg):
        e = [i for i in cg.edgeIterator(edgePredicate=lambda j: len(list(cg.edgeIterator(edgePredicate=lambda k: k[0]==j[1] and k[1]==j[0] and 'stemid' in cg.getEdgeAttr(*k))))>0) if abs(i[0]) < abs(i[1])]
        constraints = {}
        for start,end,index in e:  # @UnusedVariable
            input1 = list(cg.edgeIterator(edgePredicate=lambda i: i[1]==start and i[0]!=end and 'stemid' in cg.getEdgeAttr(*i)))
            input2 = list(cg.edgeIterator(edgePredicate=lambda i: i[1]==end and i[0]!=start and 'stemid' in cg.getEdgeAttr(*i)))
            output1 = list(cg.edgeIterator(edgePredicate=lambda i: i[0]==end and i[1]!=start and 'stemid' in cg.getEdgeAttr(*i)))
            output2 = list(cg.edgeIterator(edgePredicate=lambda i: i[0]==start and i[1]!=end and 'stemid' in cg.getEdgeAttr(*i)))
            if input1 and output1:
                middleF = list(cg.edgeIterator(edgePredicate=lambda j: j[0]==start and j[1]==end and 'stemid' in cg.getEdgeAttr(*j)))
                middleR = list(cg.edgeIterator(edgePredicate=lambda j: j[0]==end and j[1]==start and 'stemid' in cg.getEdgeAttr(*j)))
                inedge = input1
                output= output1
            else:
                middleF = list(cg.edgeIterator(edgePredicate=lambda j: j[0]==end and j[1]==start and 'stemid' in cg.getEdgeAttr(*j)))
                middleR = list(cg.edgeIterator(edgePredicate=lambda j: j[0]==start and j[1]==end and 'stemid' in cg.getEdgeAttr(*j)))
                inedge = input2
                output= output2
    
            if len(inedge)==1 and len(middleF)==1 and len(middleR)==1 and len(output)==1:
                inedge   = inedge[0]
                middleF = middleF[0]
                middleR = middleR[0]
                output  = output[0]
            
                inputcov   = cg.getEdgeAttr(*inedge)['weight']     
                middleFcov = cg.getEdgeAttr(*middleF)['weight']     
                middleRcov = cg.getEdgeAttr(*middleR)['weight']     
                outputcov  = cg.getEdgeAttr(*output)['weight']     
            
                r1 = round(middleFcov/float(inputcov))
                r2 = round(middleRcov/float(inputcov)) + 1
            
                r3 = round(middleFcov/float(outputcov))
                r4 = round(middleRcov/float(outputcov)) + 1
            
                r = int(round((r1+r2+r3+r4)/4)) - 1
                    
                constraints[cg.getEdgeAttr(*inedge)['stemid']] = [[cg.getEdgeAttr(*middleF)['stemid'],cg.getEdgeAttr(*middleR)['stemid']] * r + \
                                                                 [cg.getEdgeAttr(*middleF)['stemid'],cg.getEdgeAttr(*output)['stemid']]]
        return constraints

    def minisatSimpleConstraints(self,cg):
        e = [i for i in cg.edgeIterator(edgePredicate=lambda j: j[0]==j[1]  and 'stemid' in cg.getEdgeAttr(*j))]
        constraints = {}
        for start,end,index in e:
            inedge = list(cg.edgeIterator(edgePredicate=lambda i: i[1]==start and i[0]!=end  and 'stemid' in cg.getEdgeAttr(*i)))
            output = list(cg.edgeIterator(edgePredicate=lambda i: i[0]==end and i[1]!=start  and 'stemid' not in cg.getEdgeAttr(*i)))
        
            middle = (start,end,index)
    
            if len(inedge)==1 and len(output)==1:
                inedge   = inedge[0]
                output  = output[0]
            
                inputcov   = cg.getEdgeAttr(*inedge)['weight']     
                middlecov  = cg.getEdgeAttr(*middle)['weight']     
                outputcov  = cg.getEdgeAttr(*output)['weight']     
            
                r1 = round(middlecov/float(inputcov))            
                r2 = round(middlecov/float(outputcov))
            
                r = int(round((r1+r2)/2))
                    
                constraints[cg.getEdgeAttr(*inedge)['stemid']] = [[cg.getEdgeAttr(*middle)['stemid']] * r + \
                                                                [cg.getEdgeAttr(*output)['stemid']]]
        return constraints


        
    def pairEndedConstraints(asm,cg,threshold=5.,back=500):
    
        fork =   [e for e in cg.edgeIterator(edgePredicate=lambda i: \
                                                           'stemid' in cg.getEdgeAttr(*i) and
                                                           len(list(cg.parentIterator(i[0],
                                                                                      edgePredicate=lambda j: j[0]!=i[1] and 'stemid' in cg.getEdgeAttr(*j))
                                                                   )
                                                              )==2 
                                                       and len(list(cg.neighbourIterator(i[1],
                                                                                         edgePredicate=lambda j:j[1]!=i[0] and 'stemid' in cg.getEdgeAttr(*j))
                                                                   )
                                                              )==2
                                             )
                 ]
    
        bifork = [([cg.getEdgeAttr(*i)['stemid'] for i in 
                    cg.edgeIterator(edgePredicate=lambda j: j[1]==e[0] and j[0]!=e[1]  and 'stemid' in cg.getEdgeAttr(*j))],
                   cg.getEdgeAttr(*e)['stemid'],
                   [cg.getEdgeAttr(*i)['stemid'] for i in 
                    cg.edgeIterator(edgePredicate=lambda j: j[0]==e[1] and j[1]!=e[0]  and 'stemid' in cg.getEdgeAttr(*j))]) for e in fork]
    
        links = [(i,
                  (pairEndedConnected(asm,cg,i[0][0],i[2][0],back)[0]+
                   pairEndedConnected(asm,cg,i[0][1],i[2][1],back)[0]+0.0001)/
                  (pairEndedConnected(asm,cg,i[0][0],i[2][1],back)[0]+
                   pairEndedConnected(asm,cg,i[0][1],i[2][0],back)[0]+0.0001)) 
                 for i in bifork]
    
        constraints = {}
    
        for (starts,middle,ends),ratio in links:
            if  ratio >= threshold:
                constraints[starts[0]]=[middle,ends[0]]
                constraints[starts[1]]=[middle,ends[1]]
            elif ratio <= 1/threshold:
                constraints[starts[0]]=[middle,ends[1]]
                constraints[starts[1]]=[middle,ends[0]]
            
    
        changed=True
        while changed:
            n = iter(constraints)
            changed=False
            while not changed:
                try:
                    k=next(n)
                    nk=constraints[k][-1]
                    if nk in constraints:
                        constraints[k].extend(constraints[nk])
                        # del constraints[nk]
                        changed=True
                except StopIteration:
                    break

        for k in constraints:
            constraints[k]=[constraints[k]]

        return constraints
     
    def scaffoldConstraints(self,cg,back=500, minlink=5):
        ends = [cg.getEdgeAttr(*i)['stemid']
                for i in cg.edgeIterator(edgePredicate=lambda e: 'stemid' in cg.getEdgeAttr(*e) and len(list(cg.neighbourIterator(e[1], edgePredicate=lambda i: 'stemid' in cg.getEdgeAttr(*i))))==0)]
        starts= [cg.getEdgeAttr(*i)['stemid']
                for i in cg.edgeIterator(edgePredicate=lambda e: 'stemid' in cg.getEdgeAttr(*e) and len(list(cg.parentIterator(e[0], edgePredicate=lambda i: 'stemid' in cg.getEdgeAttr(*i))))==0)]
    
        constraints = {}
    
        for e in ends:
            for s in starts:
                if pairEndedConnected(self,cg,e,s,back)[0] >= minlink:
                    if e in constraints:
                        constraints[e].append([s])    
                    else:
                        constraints[e]=[[s]]
    
        return constraints



    
    def mergeConstraints(c1,c2):
        for k in c2:
            if k in c1:
                c1[k].extend(c2[k])
            else:
                c1[k]=c2[k]
        return c1
    
    constraints = {}
    constraints = mergeConstraints(constraints,minisatSimpleConstraints(self,cg))
    constraints = mergeConstraints(constraints,minisatDoubleConstraints(self,cg))
    constraints = mergeConstraints(constraints,pairEndedConstraints(self,cg,threshold,back))
    constraints = mergeConstraints(constraints,scaffoldConstraints(self,cg,back,minlink))
    
    interns = set()
    
    for e in constraints:
        for p in constraints[e]:
            for n in p[0:-1]:
                interns.add(n)
                
    for e in cg.edgeIterator(edgePredicate=lambda i: 'stemid' in cg.getEdgeAttr(*i)):
        stemid = cg.getEdgeAttr(*e)['stemid']
        if stemid not in constraints and stemid not in interns:
            constraints[stemid]=[[cg.getEdgeAttr(*n)['stemid']]
                                 for n in cg.edgeIterator(edgePredicate=lambda i : 'stemid' in cg.getEdgeAttr(*i) and i[0]==e[1])]
    
    return constraints

    
def estimateDeadBrancheLength(self,default=10):
    cg = self.compactAssembling(verbose=False)
    smallbranches = [i for i in [(cg.getEdgeAttr(*e)['length']) 
                            for e in cg.edgeIterator(edgePredicate=lambda e: 
                                            len(list(cg.neighbourIterator(e[1])))==0 
                                         or len(list(cg.parentIterator(e[0])))==0)]
                     if i > 1 and i < 100]
    msmallbranches = mode(smallbranches)
             
           
    # print msmallbranches, smallbranches 
                      
    # looks for small branches on the side of the main assembly                                   
    if msmallbranches is not None and msmallbranches < 100:
        msmallbranches=msmallbranches*2
    else:
        msmallbranches=default
        
    return msmallbranches

def selectGoodComponent(cg):
    
    def geneincc(cc):
        return any(cg.getEdgeAttr(*e)['ingene']>0 for e in cc)
    
    cc = list(cg.connectedComponentIterator())
    goodcc=[]
    for cc1 in cc:
        ccp = set(-i for i in cc1)
        if ccp not in goodcc:
            goodcc.append(cc1)
      
    cclength = [[cg.getEdgeAttr(*i)['length'] 
                    for i in cg.edgeIterator(nodePredicate=lambda n: n in cc1) 
                    if 'stemid' in cg.getEdgeAttr(*i)
                ] for cc1 in goodcc]
                
    ccmlength=[(sum(i)/float(len(i)),len(i)) for i in cclength]
    
    m = weightedMode(ccmlength)
    
    if m < 1000: 
        gcc = [list(cg.edgeIterator(nodePredicate=lambda n:n in c,
                                    edgePredicate=lambda e: 'stemid' in cg.getEdgeAttr(*e))) 
               for c,(mcc,lcc) in map(lambda a,b:(a,b),goodcc,ccmlength)  # @UnusedVariable
               if mcc > m * 2]
    else:
        gcc = [list(cg.edgeIterator(nodePredicate=lambda n:n in c,
                                    edgePredicate=lambda e: 'stemid' in cg.getEdgeAttr(*e))) 
               for c,(mcc,lcc) in map(lambda a,b:(a,b),goodcc,ccmlength) ]  # @UnusedVariable
    
    gcc = [cc for cc in gcc if geneincc(cc)]
        
    return gcc

# WARNING :
#threshold=5.,back=500, 
#minlink=5, limitSize=0
#
# are never used
#
def unfoldAssembling(self,assgraph,constraints=None,
                     seeds=None,threshold=5.,back=500, 
                     minlink=5, limitSize=0,
                     circular=False,
                     force=False):

    def addStepToAPath(path,step,limitSize):
        nw = dict(path[0])
        np = list(path[2]) 
        iw = path[3]
        nl = path[4]
        
        np.append(step)
        nw[abs(step)]-=iw
        ns=sum((nw[x]* length[x])**2  for x in nw)
        nl+=length[abs(step)]
                
        if ns > path[1] or (limitSize > 0 and nl > limitSize):
            rep = path
            complete=True
        else:
            rep = [nw,ns,np,iw,nl]
            complete=False
            
        return complete,rep
    
    def onexcoverage():
        readSize =self.index.getReadSize()
        icov = []

        for e in assgraph.edgeIterator():
            attr = assgraph.getEdgeAttr(*e)
            if 'path' in attr and attr['stemid'] > 0 and len(attr['path']) > readSize:
                
                path = attr['path']
                cov = [self.graph.getNodeAttr(i,)['coverage'] for i in path]
                s=0
                c = 0
                for i in range(len(cov)):
                    c+=cov[i]
                    s+=1
                    if s > readSize:
                        icov.append(c)
                        s-=1
                        c-=cov[i-readSize]                
        return mode(icov)

    
    attrs = [assgraph.getEdgeAttr(*i) 
             for i in assgraph.edgeIterator(edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))]
    attrs = dict((abs(i['stemid']),(i['length'],i['weight'])) for i in attrs)
    
    #si : stem id
    if seeds is None:
        si = set(attrs.keys())
    else:
        si = set(assgraph.getEdgeAttr(*e)['stemid'] 
                 for e in seeds 
                 if 'stemid' in assgraph.getEdgeAttr(*e))
        
    if constraints is None:
        constraints = pathConstraints(self,assgraph,threshold=threshold,back=back, minlink=minlink)
        
    weight=dict((abs(k),attrs[abs(k)][1]) for k in si)
    length=dict((abs(k),attrs[abs(k)][0]) for k in si)
    stems  = dict((assgraph.getEdgeAttr(*i)['stemid'],i) 
                  for i in assgraph.edgeIterator(edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e)))

                
    # paths if the collection of on construction path
    #     each path is constituted of five elements :
    #              - [0] the weigth directory
    #              - [1] the score of the path which have to be minimized
    #              - [2] the actual path as a sequence of stem ids
    #              - [3] the weight of the first stem in the path
    #              - [4] the total length of the path

    covone=onexcoverage()
    print("Coverage 1x = %d" % covone,file=sys.stderr)
#    paths = [[dict(weight),0,(i,),0,0] for i in si]       
    paths = [[dict(weight),0,(i,),covone,0] for i in si]       

    for p in paths:
#        p[3] = p[0][abs(p[2][0])]  # <--- Key error bug
        p[0][abs(p[2][0])]=0
        p[1]=sum((p[0][x]*length[x])**2  for x in p[0])
        p[4]=length[abs(p[2][0])]
            
    completePath=[]

    while paths:

        # I try to extend paths with constrains

        newpath=[]
        
        for p in paths:
            last = p[2][-1]
            complete=False
            if last in constraints:
                if len(constraints[last])==0:
                    completePath.append(p)
                for steps in constraints[last]:
                    lp = p
                    for step in steps:
                        complete,lp=addStepToAPath(lp,step,limitSize)
                        if complete:
                            completePath.append(lp)
                            break
                    if not complete:
                        newpath.append(lp)
                    
        paths = newpath
        newpath=[]
                
    cp={}    
    for p in completePath:
        first = stems[p[2][0]][0]
        end   = stems[p[2][-1]][1]
        closed = first==end
        if not closed:
            if circular:
                # We try to close the graph        
                c = assgraph.minpath(end,
                                     [first],
                                     edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e)
                                    )
                i = first
                ep = [i]
                while i != end and i in c[1]:
                    i=c[1][i]
                    ep.append(i)
            np = list(p[2])
            if circular:
                for x in range(len(ep)-1,0,-1):
                    s = assgraph.getEdgeAttr(ep[x],ep[x-1],0)['stemid']
                    p[0][abs(s)]-=p[3]
                    np.append(s)
            ns = sum((p[0][x]* length[x])**2  for x in p[0]) 
            first = stems[np[0]][0]
            end   = stems[np[-1]][1]
            closed = first==end
            
            if not closed and force:
                closed = True
                np.append(0)
            np = tuple(np)
        else:
            ns = p[1]
            np = p[2]
        cp[tuple(np)]=(p[0],ns,p[3],closed)
        
    cp = [(x,cp[x][1],cp[x][-1]) for x in cp]
    cp.sort(key=lambda x:x[1],reverse=True)
         
    return cp
    
    
def unfoldmarker(assgraph,seeds=None):
    
    if seeds is None:
        cc = list(assgraph.edgeIterator(edgePredicate = lambda e: 'stemid' in assgraph.getEdgeAttr(*e)))
    else:
        cc = [e for e in seeds if 'stemid' in assgraph.getEdgeAttr(*e)]

    sources = [x[0] for x in cc if assgraph.getEdgeAttr(*x)['ingene']>0]
    dests   = [x[1] for x in cc if assgraph.getEdgeAttr(*x)['ingene']>0]
    
    maxp=[]
    maxpp=0
    for s in sources:
        for d in dests:
            p = assgraph.minpath(s,[d])
            i = d
            ep = [i]
            while i != s and i in p[1]:
                i=p[1][i]
                ep.append(i)
                
            ep.reverse()
            f = ep[0]
            pp=[]
            for e in ep[1:]:
                es = list(assgraph.edgeIterator(edgePredicate=lambda i:i[0]==f and i[1]==e))
                ea = [assgraph.getEdgeAttr(*i) for i in es]
                ev = max([a['length'] * a['ingene'] for a in ea]+[0])
                pp.append(ev)
                f=e
            pp = sum(pp)
            
            
            
            if pp > maxpp or (pp==maxpp and len(ep) < len(maxp)):
                maxp=ep
                maxpp=pp
                
    cont = True
    while cont:
        p = set(assgraph.parentIterator(maxp[0]))
        if len(p)==1:
            sid = p.pop()
            if sid not in maxp:          
                maxp.insert(0,sid)
            else:
                cont=False
        else:
            cont=False

    cont = True
    while cont:
        p = set(assgraph.neighbourIterator(maxp[-1]))
        if len(p)==1:
            sid = p.pop()
            if sid not in maxp:
                maxp.append(sid)
            else:
                cont=False
        else:
            cont=False
            
    f = maxp[0]
    ep=[]
    for e in maxp[1:]:
        es = list(assgraph.edgeIterator(edgePredicate=lambda i:i[0]==f and i[1]==e))
        ea = [assgraph.getEdgeAttr(*i) for i in es]
        ge = es[0]
        a = assgraph.getEdgeAttr(*ge)
        if 'stemid' in a:
            gw = a['weight']*a['length']
            for i in es[1:]:
                a = assgraph.getEdgeAttr(*i)
                if 'stemid' in a:
                    w = a['weight']*a['length']
                    if w > gw:
                        gw=w
                        ge=i
            sid = assgraph.getEdgeAttr(*ge)['stemid']
            ep.append(sid)     
        f=e
    return ep

def estimateFragmentLength(self,minlength=1000):
    cg = self.compactAssembling(verbose=False)
    edges = [i for i in cg.edgeIterator() if cg.getEdgeAttr(*i)['length']>=minlength]
    lindex=len(self.index)
    r=self.index
    
    delta=[]
    
    for e in edges:
        stem=cg.getEdgeAttr(*e)['path']
        si = dict((stem[i],i) for i in range(len(stem)))
        for p in stem: 
            if p > 0 and p < lindex:
                delta.extend(si[i]-si[p] for i in r.normalizedPairedEndsReads(p)[1]
                             if i in si and si[i]-si[p] > 0)
                
    if delta:
        mdelta = sum(delta) / float(len(delta))
        m2delta= sum((d ** 2)  for d in delta) / len(delta)
        variance=m2delta - mdelta**2
        if variance < 0:
            variance=0
        sdelta = math.sqrt(variance)
    
        return (mdelta+self.index.getReadSize(),sdelta)
    else:
        return None,None
    
def dumpGraph(fileout,asm):
    graph = asm.graph
    index = asm.index
    readsize = index.getReadSize()

    edgeIterator = graph.edgeIterator()
    
    if isinstance(fileout, (str,bytes)):
        fileout = open(fileout,"w")
        
    for i in range(index.fakes.firstid,index.fakes.lastid):
        print('F %d %s' % (i,index.getRead(i,0,readsize).decode('ascii')),
              file=fileout
             )
    
    for f,t,l in edgeIterator:  # @UnusedVariable
        if abs(f) < abs(t):
            ea = asm.graph.getEdgeAttr(f,t,0)
            print("E",f,t,ea['coverage'],file=fileout)
    
def restoreGraph(filein,index,matches=None):
    asm     = Assembler(index) 
    readmax = len(index) + 1
  
    graph = asm.graph
    gene = matchtogene(matches)
    
    if isinstance(filein, str):
        filein = open(filein)
        
    for l in filein:
        #print(len(graph))
        if l[0]=="F":
            t,i,s = l.strip().split()
            i=int(i)
            s=bytes(s,encoding='ascii')
            rids = index.getReadIds(s)
            assert rids[0]==i
        elif l[0]=='E':
            t,f,t,c = l.strip().split()
            f = int(f)
            t = int(t)
            c = int(c)
        
            if f not in graph:
                node  = graph.addNode(f)
                node['gene']=gene.get(abs(f),None)
                node['cycle']=0
                if f < readmax:
                    node['fake5']=0
                    node['fake3']=0
                else:
                    node['graphics']={'fill':"#00FF00"}
    
            if t not in graph:
                node  = graph.addNode(t)
                node['gene']=gene.get(abs(t),None)
                node['cycle']=0
                if f < readmax:
                    node['fake5']=0
                    node['fake3']=0
                else:
                    node['graphics']={'fill':"#00FF00"}
    
            edges = graph.addEdge(f,t)
            edges[1]['coverage']=c
            edges[2]['coverage']=c
            edges[1]['label']="%s (%d)" % (edges[1]['ext'],c)
            edges[2]['label']="%s (%d)" % (edges[2]['ext'],c)

    return asm


# Experimental section, unused functions

def fillGaps2(self,minlink=5,
                  back=200,
                  kmer=12,
                  smin=40,
                  delta=0,
                  cmincov=5,
                  minread=20,
                  minratio=0.1, 
                  emincov=1,
                  maxlength=None,
                  gmincov=1,
                  minoverlap=60,
                  lowfilter=True,
                  adapters5=(),
                  adapters3=(),
                  maxjump=0,
                  snp=False,
                  nodeLimit=1000000,
                  onlyfill=False):
    '''
    
    :param minlink:
    :param back:
    :param kmer:
    :param smin:
    :param delta:
    :param cmincov:
    :param minread:
    :param minratio:
    :param emincov:
    :param maxlength:
    :param gmincov:
    :param minoverlap:
    :param lowfilter:
    :param maxjump:
    :param snp: If set to True (default value is False) erase SNP variation
                by conserving the most abundant version
    '''
    global __cacheAli
    global __cacheAli2
    __cacheAli = __cacheAli2
    __cacheAli2 = set()
    
    def isInitial(n):
        return len(list(assgraph.parentIterator(n[0],edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))))==0 
    def isTerminal(n):
        return len(list(assgraph.neighbourIterator(n[1],edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))))==0

    assgraph = self.compactAssembling(verbose=False)
    
    index = self.index
    
    ei = [i for i in assgraph.edgeIterator(edgePredicate=isInitial)]
    et = [i for i in assgraph.edgeIterator(edgePredicate=isTerminal)]
    
    eiid = [assgraph.getEdgeAttr(*i)['stemid'] for i in ei]
    etid = [assgraph.getEdgeAttr(*i)['stemid'] for i in et]

    epi = [set(assgraph.getEdgeAttr(*i)['path'][0:back]) for i in ei]
    ept = [set(assgraph.getEdgeAttr(*i)['path'][-back:]) for i in et]

    eei = [set(assgraph.getEdgeAttr(*i)['path'][0:100]) for i in ei]
    eet = [set(assgraph.getEdgeAttr(*i)['path'][-100:]) for i in et]
    
    exi = [getPairedRead(self,assgraph,i,back,end=False) for i in eiid]
    ext = [getPairedRead(self,assgraph,i,back,end=True) for i in etid]
    
    nei = len(ei)
    net = len(et)
    s=[]
    maxcycle=max(self.graph.getNodeAttr(i)['cycle'] for i in self.graph)
    lassemb = len(self)
    cycle = maxcycle
    linked=set()
    extended=set()
    for e1 in range(net):
        for e2 in range(nei):
            connected = et[e1][1]==ei[e2][0]
            if not connected:
                linkedby,ml,sl  = pairEndedConnected(self,assgraph,etid[e1],eiid[e2],back)
            
                if linkedby >= minlink and abs(etid[e1]) <= abs(eiid[e2]):
                    extended.add(etid[e1])
                    extended.add(-eiid[e2])
                    if (etid[e1],eiid[e2]) not in linked:
                        linked.add((-eiid[e2],-etid[e1]))
                        print("\n\nLinking Stems %d -> %d" % (etid[e1],eiid[e2]),
                              file=sys.stderr)

                        ex = frozenset(((ext[e1] | exi[e2]) - ept[e1] - epi[e2]) | eet[e1] | eei[e2])
                        
                        ingraph = sum(i in self.graph for i in ex)
                        nreads = len(ex)
                        if ingraph < nreads:
                            print ("--> %d | %d = %d reads to align (%d already assembled)" % (len(ext[e1]),len(exi[e2]),nreads,ingraph),
                                  file=sys.stderr)

                            if nreads > 10:
                                __cacheAli2.add(ex)
                                if ex not in __cacheAli:
                                    ali= multiAlignReads(ex,index,kmer,smin,delta)
                                    print('',file=sys.stderr)
                
                                    goodali = [i for i in ali if len(i) >= nreads/4]
                                    print("--> %d consensus to add" % len(goodali),
                                          file=sys.stderr)

                                    for a in goodali:
                                        cycle+=1
                                        c = consensus(a,index,cmincov)
                                        s = insertFragment(self,c,cycle=cycle)
                                        print("     %d bp (%d reads) added on cycle %d" % (len(c),len(s),cycle),
                                              file=sys.stderr)

            
                                        a = tango(self,
                                                  seeds      = s,
                                                  minread    = minread,
                                                  minratio   = minratio,
                                                  mincov     = emincov,
                                                  minoverlap = minoverlap,
                                                  lowfilter  = lowfilter,
                                                  adapters5   = adapters5,
                                                  adapters3   = adapters3,
                                                  maxjump    = maxjump,
                                                  cycle      = cycle,
                                                  nodeLimit  = nodeLimit)
                                        
                                        print('',file=sys.stderr)
                                else:
                                    print("--> already aligned",file=sys.stderr)

    if (not onlyfill):
        for e1 in range(net):
            if etid[e1] not in extended:
                print("\n\nExtending Stems %d" % (etid[e1]),
                      file=sys.stderr)
    
                ex = frozenset((ext[e1] - ept[e1]) | eet[e1])
                nreads = len(ex)
                print("--> %d reads to align" % (nreads),
                      file=sys.stderr)
    
                if nreads > 10:
                    __cacheAli2.add(ex)
                    if ex not in __cacheAli:
                        ali= multiAlignReads(ex,index,kmer,smin,delta)
                        print('',file=sys.stderr)
                        goodali = [i for i in ali if len(i) >= nreads/4]
                        print("--> %d consensus to add" % len(goodali),
                              file=sys.stderr)
    
                        for a in goodali:
                            c = consensus(a,index,cmincov)
                            if c:
                                cycle+=1
                                s = insertFragment(self,c,cycle=cycle)
                                print("     %d bp (%d reads) added on cycle %d" % (len(c),len(s),cycle),
                                      file=sys.stderr)
    
                                a = tango(self,
                                          seeds      = s,
                                          minread    = minread,
                                          minratio   = minratio,
                                          mincov     = emincov,
                                          minoverlap = minoverlap,
                                          lowfilter  = lowfilter,
                                          adapters5  = adapters5,
                                          adapters3  = adapters3,
                                          maxjump    = maxjump,
                                          cycle      = cycle,
                                          nodeLimit  = nodeLimit)
                            print("",file=sys.stderr)
                    else:
                        print("--> already aligned",file=sys.stderr)

    self.cleanDeadBranches(maxlength=10)
    cutLowCoverage(self,gmincov,terminal=True)
#    cutLowCoverage(self,int(gmincov/3),terminal=False)   
    
    if maxlength is not None:
        smallbranches = maxlength
    else:
        smallbranches = estimateDeadBrancheLength(self)
        print("     Dead branch length setup to : %d bp" % smallbranches,
              file=sys.stderr)

    self.cleanDeadBranches(maxlength=smallbranches)

    if snp:
        cutSNPs(self)

    newnodes = len(self) - lassemb
    
    print('',file=sys.stderr)
    print("#######################################################",file=sys.stderr)
    print("#",file=sys.stderr)
    print("# Added : %d bp (total=%d bp)" % (newnodes/2,len(self)/2),file=sys.stderr)
    print("#",file=sys.stderr)
    print("#######################################################",file=sys.stderr)
    print('',file=sys.stderr)
    
    return newnodes

def cutHighCoverage(self,maxcov,terminal=True):
    def isTerminal(g,n):
        return len(list(g.parentIterator(n)))==0 or len(list(g.neighbourIterator(n)))==0
    
    def endnodeset(g):
        return set(g.nodeIterator(predicate = lambda n : (len(list(g.neighbourIterator(n)))==0)))
    
    def startnodeset(g):
        return set(g.nodeIterator(predicate = lambda n : (len(list(g.parentIterator(n)))==0)))
    
    
    if terminal:
        tstates=[True]
    else:
        tstates=[True,False]
    ilength=len(self)
    cg = self.compactAssembling(verbose=False)
    index = self.index
    readSize = index.getReadSize()
    for terminal in tstates:
        print('',file=sys.stderr)
        if terminal:
            print("Deleting terminal branches",file=sys.stderr)
        else:
            print("Deleting internal branches",file=sys.stderr)
        extremities = endnodeset(cg) | startnodeset(cg)
        go = True
        while go:
            go = False
            stems = [x for x in cg.edgeIterator() 
                     if not terminal or (isTerminal(cg, x[0]) or isTerminal(cg, x[1]))]
            if stems:
                stems.sort(key=lambda i:cg.getEdgeAttr(*i)['weight'])
                heaviest = stems.pop()
                lattr = cg.getEdgeAttr(*heaviest)
#                 print >>sys.stderr
#                 print >>sys.stderr,lattr['stemid'],len(stems),lightest[0],lightest[1],lattr['weight']
        #         print >>sys.stderr,lattr['weight'] < mincov
        #         print >>sys.stderr,isTerminal(cg, lightest[0]), isTerminal(cg, lightest[1])
        #         print >>sys.stderr,lattr['weight'] < mincov and ((not terminal) or isTerminal(cg, lightest[0]) or isTerminal(cg, lightest[1]))
        #         print >>sys.stderr
                if lattr['weight'] > maxcov: 
                    if stems:
                        go=True
                    for n in lattr['path'][1:-1]:
                        if n in self.graph:
                            del self.graph[n]
                    if heaviest[0] in extremities and heaviest[0] in self.graph:
                        del self.graph[heaviest[0]]
                    if heaviest[1] in extremities and heaviest[1] in self.graph:
                        del self.graph[heaviest[1]]
                        
                    print("Remaining edges : %d node : %d" % (self.graph.edgeCount(),len(self)),
                          end='\r',
                          file=sys.stderr)
        
                    cg.deleteEdge(*heaviest)
                    tojoin=[]
                    if heaviest[0] in extremities:
                        del cg[heaviest[0]]
                    else:
                        tojoin.append(heaviest[0])
                    if heaviest[1] in extremities:
                        del cg[heaviest[1]]
                    else:
                        tojoin.append(heaviest[1])
#                    print >>sys.stderr,lightest[0] in extremities,lightest[1] in extremities,tojoin
                    for c in tojoin:
                        begin = list(cg.parentIterator(c))
                        end   = list(cg.neighbourIterator(c))
                        if len(begin)==1 and len(end)==1:
                            begin = begin[0]
                            end = end[0]
                            e1s = list(cg.edgeIterator(edgePredicate = lambda e:e[0]==begin and e[1]==c))
                            e2s = list(cg.edgeIterator(edgePredicate = lambda e:e[0]==c and e[1]==end))
                            if len(e1s)==1 and len(e2s)==1:
                                e1 = e1s[0]
                                e2 = e2s[0]
                                attr1 = cg.getEdgeAttr(*e1)
                                
                                attr2 = cg.getEdgeAttr(*e2)
                                lentot= attr1['length'] + attr2['length']
                                weight= float(attr1['weight'] * attr1['length'] + attr2['weight'] * attr2['length'])/lentot
#                                     print >>sys.stderr
#                                     print >>sys.stderr,"(",attr1['weight'],"*", attr1['length'], '+',attr2['weight'],"*",attr2['length'],")/",lentot,"=",weight
#                                     time.sleep(1)
                                sequence=attr1['sequence'] + attr2['sequence']
                                stemid=lattr['stemid']
                                path=attr1['path'] + attr2['path'][1:]
                                graphics={'width':int(weight/readSize)+1,
                                          'arrow':'last'}
                        
                                if lentot > 10:
                                    label="%d : %s->(%d)->%s  [%d]" % (stemid,
                                                                       sequence[0:5].decode('ascii'),
                                                                       lentot,
                                                                       sequence[-5:].decode('ascii'),
                                                                       weight)
                                else:
                                    label="%d : %s->(%d)  [%d]" % (stemid,
                                                                   sequence.decode('ascii'),
                                                                   lentot,
                                                                   weight)
                                
#                                print >>sys.stderr,"Adding merged edge -->",stemid,begin,end,weight
                                attr = cg.addEdge(begin,end)
                                attr['sequence']=sequence
                                attr['stemid']=stemid
                                attr['path']=path
                                attr['length']=lentot
                                attr['weight']= weight
                                attr['graphics']=graphics
                                attr['label']=label

                                cg.deleteEdge(*e2)                                        
                                cg.deleteEdge(*e1)  
                                del cg[c]
                                      
                                
    print('',file=sys.stderr)      
    return ilength - len(self)

def path2sam(self,assgraph,path,identifier="contig",minlink=10,nlength=20,back=200):
    '''
    Convert a path in an compact assembling graph in a fasta formated sequences.
    
    :param assgraph: The compact assembling graph as produced by the
                     :py:meth:`~orgasm.assembler.Assembler.compactAssembling` method
    :type assgraph:  :py:class:`~orgasm.graph.DiGraphMultiEdge`
    :param path:     an ``iterable`` providing an ordered list of ``stemid`` indicating
                     the path to follow.  
    :type path:      an ``iterable`` over :py:class:`int`
    :param identifier: the identifier used in the header of the fasta formated sequence
    :type identifier:  :py:class:`bytes`
    :param minlink:  the minimum count of pair ended link to consider 
                     for asserting the relationship
    :type minlink:   :py:class:`int`
    :param nlength:  how many ``N`` must be added between two segment of sequences only connected
                     by pair ended links
    :type nlength:   :py:class:`int`
    :param back:     How many base pairs must be considered at the end of each edge
    :type back:      :py:class:`int`
    
    :returns: a string containing the fasta formated sequence
    :rtype: :py:class:`bytes`

    :raises: :py:class:`AssertionError`
    '''
    
    alledges = dict((assgraph.getEdgeAttr(*e)['stemid'],e) 
                    for e in assgraph.edgeIterator(edgePredicate = lambda i: 'stemid' in assgraph.getEdgeAttr(*i)))
        
    slength=[]
    seq=[]
    oldstem=None
    oldid=None
    
    circular = alledges[path[-1]][1]==alledges[path[0]][0]
    
    if circular:
        POS = -self.index.getReadSize()
    else:
        POS = 0
    

    for stemid in path:
        stem = alledges[stemid]
        attr = assgraph.getEdgeAttr(*stem)
        

        if oldstem is not None:
            if oldstem[1]==stem[0]:
#                addInFront=False
                print("Both segments %d and %d are connected" % (oldid,stemid),file=sys.stderr)
            else:
#                addInFront=True
                connected,ml,sl = pairEndedConnected(self,assgraph,oldid,stemid,back)
                print("Both segments %d and %d are disconnected" % (oldid,stemid),file=sys.stderr)
                if connected >= minlink:
                    print("But linked by %d pair ended links" % connected,file=sys.stderr)
                    POS+=nlength
                    connected=True
                else:
                    connected=False
                    raise AssertionError('Disconnected path between stem '
                                         '%d and %d only %d pair ended links' % (oldid,stemid,connected))
        elif circular:
#            addInFront=False
            connected=True
        else:
            connected=False
#            addInfront=True
        
        
        seq.append(attr['sequence'])
        slength.append(attr['length'])
        
        oldstem = stem
        oldid=stemid
        
    s1 = alledges[path[-1]]
    s2 = alledges[path[0]]
    sid1=assgraph.getEdgeAttr(*s1)['stemid']
    sid2=assgraph.getEdgeAttr(*s2)['stemid']
    connected,ml,sl = pairEndedConnected(self,assgraph,sid1,sid2,back)
    
    if s1[1]==s2[0]:
        print("Path is circular",file=sys.stderr)
    else:
        if connected >= minlink:
            print("Path is circular but disconnected",file=sys.stderr)
            print("Linked by %d pair ended links" % connected,file=sys.stderr)
            seq.append(b'N'*nlength)
        else:
            print("Path is linear",file=sys.stderr)
            
    length = sum(slength)
    
    sam  = ["""@HD\tVN:1.5\tSO:coordinate""",
            """@SQ SN:%s LN:%s""" % (identifier,length)
           ]
    
    sam.extend(seq)
    
    return "\n".join(sam)

def stem2fasta(self):
    assgraph = self.compactAssembling(verbose=False)
    si = assgraph.edgeIterator(edgePredicate=lambda e: 'stemid' in assgraph.getEdgeAttr(*e))
    seqs = []
    for s in si:
        sattr = assgraph.getEdgeAttr(*s)
        seq = sattr["sequence"]
        seq = b'\n'.join([seq[i:(i+60)] for i in range(0,len(seq),60)])
        stemid = sattr['stemid']
        if stemid < 0:
            identifier = "edge_%d_comp" % -stemid
        else:
            identifier = "edge_%d" % stemid
        title = ">%s stemid=%d; seq_length=%d; coverage=%d; %s\n" % (identifier,stemid,sattr['length'],sattr['weight'],sattr['label'])
        seqs.append(title + seq.decode('ascii'))
        
    return '\n'.join(seqs)

