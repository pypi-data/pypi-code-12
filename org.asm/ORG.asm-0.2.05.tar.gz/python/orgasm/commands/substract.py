'''
Created on 28 sept. 2014

@author: coissac
'''


__title__="Substract an assembly from an read index"

from orgasm import getIndex,getSeeds
from orgasm.backtranslate.fasta import fasta
from orgasm.tango import restoreGraph

from subprocess import Popen
from tempfile   import mkdtemp
from tempfile   import mktemp
from shutil     import rmtree

import atexit
import os.path
import sys
import math


default_config = { "assembly" : None,
                   'sequence' : None,
                   "circular" : False
                 }

tmpdir = []

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='substract:newindex',  metavar='newindex', 
                        help='name of the new read index')
    
    
    parser.add_argument('--assembly',"-a",    dest ='substract:assembly', 
                                              metavar='assembly', 
                                              action='store',
                                              default=None, 
                                              type=str, 
                        help='The result of an assembly to substract from the read index')
    
    parser.add_argument('--sequence',"-s",    dest ='substract:sequence', 
                                              metavar='sequence', 
                                              action='store',
                                              default=None, 
                                              type=str, 
                        help='A fasta file containing sequences to substract from the read index')

    parser.add_argument("--circular","-c",
                        dest="substract:circular",
                        action='store_true',
                        default=None,
                        help='The fasta sequence file contains circular sequences'
                       )

def formatFastq(seq):
    
    fastq = '@{id:0>7}\n{seq}\n+\n{qual}'
    return fastq.format(id=seq[0],
                        seq=seq[1].decode('ascii'),
                        qual='0'*len(seq[1]))

def postponerm(filename):
    def trigger():
        print("Deleting tmp file : %s" % filename,file=sys.stderr)
        try:
            os.unlink(filename)
        except:
            pass
        
    return trigger

def postponermdir(filename):
    def trigger():
        print("Deleting tmp directory : %s" % filename,file=sys.stderr)
        try:
            rmtree(filename)
        except:
            pass
        
    return trigger

def getTmpDir():
    global tmpdir

    if not tmpdir:
        tmpdir.append(mkdtemp())
        atexit.register(postponermdir(tmpdir[0]))
        
    return tmpdir[0]


def writeToFifo(index,excluded,forward,reverse,logger):
    logger.info("Forward tmp file : %s" % forward)
    logger.info("Reverse tmp file : %s" % reverse)

    maxreadid = len(index)+1
    readlength= index.getReadSize()
    step=10 ** math.floor(math.log10(maxreadid))

    with open(forward,'w') as f, \
         open(reverse,'w') as r:
        
        j=0
        printed=set()
        logger.info('%d sequence pairs written' % 0)
        
        for i in range(1,maxreadid):
            ri=index.getPairedRead(i)

            if (not (i in printed  or abs(ri) in printed or
                     i in excluded or abs(ri) in excluded)):    
                    
                forward = index.getRead(i,0,readlength)
                reverse = index.getRead(ri,0,readlength)
                
                printed.add(i)
                printed.add(abs(ri))
                
#                logger.info("coucou1")
                print(formatFastq((i,forward)), file=f)
#                logger.info("coucou2")
                print(formatFastq((ri,reverse)),file=r)
                logger.info("coucou3")

                if not j % step:
                    logger.info('%d sequence pairs written' % j)
                j+=1
    
        

def run(config):
    
    logger=config['orgasm']['logger']
    progress = config['orgasm']['progress']
    circular = config['substract']['circular']
    output   = config['substract']['newindex']
    
    r = getIndex(config)
    maxreadid = len(r)
    readlength= r.getReadSize()

    if config['substract']['assembly'] is not None:
        assembly="%s.oas/assembling.oax"  % config['substract']['assembly']

        if not os.path.exists(assembly):
            raise RuntimeError("Cannot load the assembly %s" % config['substract']['assembly'])
        
        ecoverage,x,newprobes = getSeeds(r,config)
        asm = restoreGraph(assembly,r,x)
        
        graph = asm.graph
        readids = set(abs(x) for x in graph.nodeIterator() if not r.fakes.isFake(x))

        print(len(asm))

                      
    elif config['substract']['sequence'] is not None:
        
        sequences = fasta(config['substract']['sequence'])
        
        readids = set()
        for seq in sequences.values():
            if circular:
                seq = seq+seq[0:readlength]
            for p in range(len(seq)-readlength):
                read   = seq[p:(p+readlength)]
                rid = r.getReadIds(read)[0]
                if not r.fakes.isFake(rid):
                    readids.add(abs(rid))

    allreads=set()
    
    for rid in readids:
        allreads|=set(abs(x) for x in r.getIds(rid)[2])
        paired = set(r.normalizedPairedEndsReads(rid)[1]) | set(r.normalizedPairedEndsReads(-rid)[1])
        for prid in paired:
            allreads|=set(abs(x) for x in r.getIds(prid)[2])
            
    tmpdir = getTmpDir()
    forward = mktemp(prefix="forward-", dir=tmpdir)
    atexit.register(postponerm(forward))

    reverse = mktemp(prefix="reverse-", dir=tmpdir)
    atexit.register(postponerm(reverse))
        
    os.mkfifo(forward)
    os.mkfifo(reverse)
    
    if not os.path.exists('%s.odx' % output ):
        os.makedirs('%s.odx' % output ) 

    command = ['orgasmi','-o','%s.odx/index'  % output]
    
    command.append(forward)
    command.append(reverse)

    logger.info(' '.join(command))

    try:
        logger.info("Starting indexing...")
        process=Popen(command)
        writeToFifo(r,allreads,forward,reverse,logger)
        process.wait()
        logger.info('Done.')
    except BrokenPipeError:
        process.wait()
        logger.info('Done.')
        logger.warning("Maximum count of read indexed.")
        logger.warning("Indexing stopped but the index is usable.")
