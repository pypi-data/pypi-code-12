'''
Created on 28 sept. 2014

@author: coissac
'''
from orgasm import getOutput,getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
    scaffold, selectGoodComponent

__title__="Print some statistics about the assembling graph"

default_config = { 
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='<output>', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    parser.add_argument('--back',             dest='orgasm:back', 
                                              metavar='<insert size>',
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')

    


def run(config):

    logger=config['orgasm']['logger']
    output = getOutput(config)

    r = getIndex(config)
    ecoverage,x,newprobes = getSeeds(r,config)  
    
    asm = restoreGraph(output+'.oax',r,x)
    
    logger.info("Evaluate fragment length")
    
    meanlength,sdlength = estimateFragmentLength(asm)
    
    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300

    cg = asm.compactAssembling(verbose=False)
    
    genesincontig(cg,r,x)

    scaffold(asm,cg,minlink=5,back=int(back),addConnectedLink=False)

    ccs = list(cg.connectedComponentIterator())
    gcc = selectGoodComponent(cg)
    gnode=set()
    for cc in gcc:
        for e in cc:
            gnode.add(e[0])
            gnode.add(e[1])
    
    ucc = set()
    for cc in ccs:
        ccc = frozenset([-x for x in cc])
        if ccc not in ucc:
            ucc.add(frozenset(cc))
        

    output = open(output+".stats","w")

    print ("AssembledBasePairs:",len(asm)/2,file=output)
    print ("TotalConnectedComponents:",len(ccs),file=output)
    print ("UniqueConnectedComponents:",len(ucc),file=output)
    print ("GoodConnectedComponents:",len(ucc),file=output)
    print ("CompactNodes:",len(cg),file=output)
    print ("GoodCompactNodes:",len(gnode),file=output)
    print ("CompactEdges:",cg.edgeCount(),file=output)
    print ("GoodCompactEdges:",sum(len(x) for x in gcc),file=output)
    print ("FragmentMeanLength:",meanlength,file=output)
    print ("FragmentSdLength:",sdlength,file=output)
    
    
    

              
