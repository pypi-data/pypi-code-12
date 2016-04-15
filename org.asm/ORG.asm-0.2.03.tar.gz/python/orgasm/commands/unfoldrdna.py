'''
Created on 28 sept. 2014

@author: coissac
'''
import sys

from orgasm import getOutput,getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
    scaffold, path2fasta, unfoldmarker

__title__="Assembling graph unfolder for the nuclear rDNA complex"

default_config = {
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='output', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    parser.add_argument('--back',             dest='orgasm:back', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')
    
    parser.add_argument('--set-tag','-S',     dest ='fasta:tags', 
                                              metavar='tag', 
                                              action='append',
                                              default=[], 
                                              type=str, 
                        help='Allows to add a tag in the OBITools format '
                             'to the header of the fasta sequences')


def selectGoodComponent(cg):
    
    def geneincc(cc):
        return any(cg.getEdgeAttr(*e)['ingene']>0 for e in cc)
    
    cc = list(cg.connectedComponentIterator())
    goodcc=[]
    for cc1 in cc:
        ccp = set(-i for i in cc1)
        if ccp not in goodcc:
            goodcc.append(cc1)
      
    gcc = [list(cg.edgeIterator(nodePredicate=lambda n:n in c,
                                edgePredicate=lambda e: 'stemid' in cg.getEdgeAttr(*e))) 
           for c in goodcc] 
    
    gcc = [cc for cc in gcc if geneincc(cc)]

    return gcc
    


def run(config):

    logger=config['orgasm']['logger']
    output = getOutput(config)

    r = getIndex(config)
    coverage,x,newprobes = getSeeds(r,config)  
    
    asm = restoreGraph(output+'.oax',r,x)

    logger.info("Evaluate fragment length")
    
    meanlength,sdlength = estimateFragmentLength(asm)
    
    if meanlength is not None:
        logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))

    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300
        
    logger.info("Evaluate pair-end constraints")
    
    cg = asm.compactAssembling(verbose=False)
    
    genesincontig(cg,r,x)

    scaffold(asm,cg,minlink=5,back=int(back),addConnectedLink=False)
     
    fastaout = open(output+".fasta","w")
    fastaout = sys.stdout

    pathout  = open(output+".path","w")
    
    logger.info("Select the good connected components")
    gcc = selectGoodComponent(cg)
    
    logger.info("Print the result as a fasta file")
    
    c=1
    seqid = config['orgasm']['outputfilename'].split('/')[-1]

    for seeds in gcc:
        path = unfoldmarker(cg,seeds=seeds)
                
        fa = path2fasta(asm,cg,path,
             identifier="%s_%d" % (seqid,c),
             back=back,
             minlink=config['orgasm']['minlink'],
             logger=logger,
             tags=config['fasta']['tags'])
        
        print(fa, file=fastaout)
        print(" ".join([str(x) for x in path]),file=pathout)
        c+=1
        
    print(cg.gml(),file=open(output +'.path.gml','w'))

              
