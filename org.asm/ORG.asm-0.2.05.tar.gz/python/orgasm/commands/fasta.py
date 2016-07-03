'''
Created on 26 nov. 2014

@author: boyer
'''
from orgasm import getOutput,getIndex, getSeeds
from orgasm.tango import restoreGraph, genesincontig
from orgasm.utils import tags2str
import os
import sys


__title__="Build a fasta file from the assembling graph"

default_config = { 'tags'      : None,
                   'extension' : None
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='<index>', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='<output>', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    parser.add_argument('--set-tag','-S',     dest ='fasta:tags', 
                                              metavar='tag', 
                                              action='append',
                                              default=[], 
                                              type=str, 
                        help='Allows to add a tag in the OBITools format '
                             'to the header of the fasta sequences')

    parser.add_argument('--no-5ext',             dest='fasta:extension', 
                                              action='store_false', 
                                              default=True, 
                        help="Do not add the 5' end of the sequences")


def fastaFormat(edge, title=None,  nchar=60, extension=False,tags=[]):
    
    if title is None:
        title = 'Seq'
    
    lheader = []
        
    for k in ('weight', 'label', 'length', 'stemid', 'ingene'):
        lheader.append('%s=%s'%(k, edge[k]))
    
        
    l = ['; '.join(lheader)+"; " + tags2str(tags)]
    
    l[0] = '>%s_%d %s'%(title, edge['stemid'], l[0])

    
    seq  = edge['sequence']
    if extension:
        seq=edge['head'].lower() + seq
    lseq = len(seq)
    i=0
    while i < lseq:
        l.append(seq[i:i+60].decode('ascii'))
        i += 60
        
    return '\n'.join(l)

def run(config):

    logger=config['orgasm']['logger']
    output = getOutput(config)

    r = getIndex(config)
    ecoverage,x,newprobes = getSeeds(r,config)  
    
    asm = restoreGraph(output+'.oax',r,x)

    cg = asm.compactAssembling(verbose=False)
    
    genesincontig(cg,r,x)

#    fastaout = open(output+".fasta","w")
    fastaout = sys.stdout
        
    logger.info("Print the result as a fasta file")



    edges = [cg.getEdgeAttr(*i) for i in cg.edgeIterator(edgePredicate = lambda e : cg.getEdgeAttr(*e)['stemid']>0)]
    head, tail = os.path.split(config['orgasm']['outputfilename'])
    c=1
    for e in edges:
        print(fastaFormat(e, "%s_%d" % (tail,c),
                          extension=config['fasta']['extension'],
                          tags=config['fasta']['tags']
                          ),
              file=fastaout)
        c+=1
        

