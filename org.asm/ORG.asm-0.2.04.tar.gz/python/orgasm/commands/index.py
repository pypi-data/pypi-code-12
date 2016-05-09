'''
Created on 28 sept. 2014

@author: coissac
'''

from subprocess import Popen
from tempfile   import mkdtemp
from tempfile   import mktemp
from shutil     import rmtree
from urllib.request import urlopen

import atexit
import os
import os.path
import sys
import re

from orgasm.utils.dna import reverseComplement  # @UnresolvedImport
#from orgasm.files import uopen

import zlib
from collections import Counter, deque
from sys import stderr

from orgasm.indexer import Index

__title__="Index a set of reads"

default_config = { 'reformat' : False,
                   'single'   : False,
                   'forward'  : None,
                   'reverse'  : None,
                   'maxread'  : None,
                   'length'   : None,
                   'estimate' : None,
                   'fasta'    : False,
                   'ffasta'   : False,
                   'rfasta'   : False,
                   'nopipe'   : False,
                   'checkpairs':False,
                   'mate'     : False,
                   'checkids' : False
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='name of the produced index')

    parser.add_argument(dest='index:forward',  metavar='forward', 
                        nargs='?', 
                        default=None,
                        help='Filename of the forward reads')
    
    parser.add_argument(dest='index:reverse',     
                        metavar='reverse', 
                        nargs='?', 
                        default=None,
                        help='Filename of the reverse reads' )
    
    
    parser.add_argument("--reformat",
                        dest="index:reformat",
                        action='store_true',
                        default=None,
                        help='Asks for reformatting an old sequence index to the new format'
                       )
    
    parser.add_argument('--single',           
                        dest='index:single', 
                        action='store_true', 
                        default=None, 
                        help='Single read mode')

    parser.add_argument('--mate-pairs',       dest='index:mate', 
                                              action='store_true', 
                                              default=None, 
                        help='Mate pair library mode')

    parser.add_argument('--check-ids',       dest='index:checkids', 
                                              action='store_true', 
                                              default=False, 
                        help='Checks that forward and reverse ids are identical')

    parser.add_argument('--max-read',         dest='index:maxread', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the count of million of reads to '
                             'index (default the full file)')
    
    parser.add_argument('--length',           dest='index:length', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='The length of the read to index '
                             ' (default indexed length is estimated from the first read)')
    
    parser.add_argument('--estimate-length',  dest='index:estimate', 
                                              metavar='FRACTION',
                                              type=float, 
                                              action='store', 
                                              default=None, 
                        help='Estimate the length to index for conserving FRACTION '
                             'of the overall dataset')
    
    parser.add_argument('--fasta',            dest='index:fasta', 
                                              action='store_true', 
                                              default=None, 
                        help='forward and reverse sequence files are fasta formated')

    parser.add_argument('--no-pipe',          dest='index:nopipe', 
                                              action='store_true', 
                                              default=None, 
                        help='do not use pipe but temp files instead')

    parser.add_argument('--forward-fasta',            dest='index:ffasta', 
                                              action='store_true', 
                                              default=False, 
                        help='forward file is a fasta file')

    parser.add_argument('--check-pairing',            dest='index:checkpairs', 
                                              action='store_true', 
                                              default=False, 
                        help='ensure that forward and reverse files are correctly paired')

    parser.add_argument('--reverse-fasta',            dest='index:rfasta', 
                                              action='store_true', 
                                              default=False, 
                        help='reverse file is a fasta file')
tmpdir = []

# @atexit.register
# def cleanup():
#     try:
#         os.unlink(FIFO)
#     except:
#         pass

def reformatOldIndex(config):

    logger  = config['orgasm']['logger']
    output  = config['orgasm']['indexfilename']
    if not (os.path.exists('%s.ofx' % output ) and
            os.path.exists('%s.ogx' % output ) and
            os.path.exists('%s.opx' % output ) and
            os.path.exists('%s.orx' % output )
           ):
        logger.error('The %s index does not exist or is not complete' % output)
        sys.exit(1)
    
    dirname = '%s.odx' % output
    if not os.path.exists(dirname):
        os.makedirs(dirname) 

    os.rename('%s.ofx' % output, '%s/index.ofx' % dirname)
    os.rename('%s.ogx' % output, '%s/index.ogx' % dirname)
    os.rename('%s.opx' % output, '%s/index.opx' % dirname)
    os.rename('%s.orx' % output, '%s/index.orx' % dirname)

    sys.exit(0)

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

def allopen(filename):
    try:
        f = urlopen(filename)
    except:
        f = open(filename,newline=None)
        

    return f


def ungzip(filename,nopipe):
    tmpdir = getTmpDir()

    fifo = mktemp(prefix="unziped-", dir=tmpdir)
    command="gzip -d -c %s > %s" % (filename,fifo)
    
    if nopipe:
        os.system(command)
    else:
        os.mkfifo(fifo)
        process = Popen(command,                                            # @UnusedVariable
                        shell=True,
                        stderr=open('/dev/null','w')) 
    
    atexit.register(postponerm(fifo))

    return fifo

def unbzip(filename,nopipe):
    tmpdir = getTmpDir()

    fifo = mktemp(prefix="unziped-", dir=tmpdir)
    command="bzip2 -d -c %s > %s" % (filename,fifo)
    atexit.register(postponerm(fifo))
    
    if nopipe:
        os.system(command)
    else:
        os.mkfifo(fifo)
        process = Popen(command,                                            # @UnusedVariable
                        shell=True,
                        stderr=open('/dev/null','w')) 
    
    return fifo
    

    
def readFasta(filename):
    
    if isinstance(filename, str):
        filename = open(filename)
    
    seq = []    
    sid = ""
    seqid=0
    
    for line in filename:
        if line[0]==">":
            if seqid > 0:
                seq = ''.join(seq)
                yield (sid,bytes(seq,encoding='latin1'))
            sid = line[1:].split(None,1)[0].rsplit('/',1)[0].strip()
            seqid+=1
            seq=[]
        else:
            seq.append(line.strip().upper())
            
    seq = ''.join(seq)
    yield (sid,bytes(seq,encoding='latin1'))
           
def readFastq(filename):
    
    if isinstance(filename, str):
        filename = open(filename)
        
    seq   = []
    seqid = 0
    lseq  = 0
    sid   = ""
    
    for line in filename:
        if line[0]=="@":
            if seqid > 0:
                seq = ''.join(seq)
                yield (sid,bytes(seq,encoding='ascii'))
            sid = line[1:].split(None,1)[0].rsplit('/',1)[0].strip()
            seqid+=1
            lseq = 0
            seq=[]
        elif line[0]!='+':
            seq.append(line.strip().upper())
            lseq+=1
        else:
            for i in range(lseq):  # @UnusedVariable
                next(filename)
        
    seq = ''.join(seq)
    yield (sid,bytes(seq,encoding='latin1'))
    

def acgtCut(seqs):
    acgt = re.compile(b'[ACGT]+')
    
    for s in seqs:
        m = acgt.findall(s[1])
        bs=''
        for ss in m:
            if len(ss) > len(bs):
                bs=ss
        yield (s[0],bs)
        
def lengthStats(seqs):
    
    store=[]
    
    def seqIterator():
        for s in store:
#            print(s)
            if s[1] is not None:
                yield (s[0],zlib.decompress(s[1]))
            else:
                yield (s[0],b'')
            
    def reader():
        for s in seqs:
#            print(s)
            if len(s[1]):
                store.append((s[0],zlib.compress(s[1])))
            else:
                store.append((s[0],None))                
            yield len(s[1])
            
    stats = Counter(reader())
    
    return stats,seqIterator()
            
def formatFastq(seq):
    
    fastq = '@{id:0>7}\n{seq}\n+\n{qual}'
    return fastq.format(id=seq[0],
                        seq=seq[1].decode('ascii'),
                        qual='0'*len(seq[1]))
               
        
def singleToPairedEnd(seqs,length):
    
    for s in seqs:
        f = s[1][0:length]
        r = reverseComplement(s[1][-length:])
        yield ((s[0],f),(s[0],r))
        
def doubleToPairedEnd(forward,reverse,checkids=False):

    for f in forward:
        r = next(reverse)
#        print "\n\n",f[0],r[0],"\n\n"
        assert not checkids or f[0]==r[0]
        yield ((f[0],f[1]),(f[0],r[1]))
        
def doubleToCheckedPairs(forward,reverse,mate=False):
    rstore = {}
    
    for seq in reverse:
        rstore[seq[0]]=zlib.compress(seq[1])
        
    for seq in forward:
        sid = seq[0]
        if sid in rstore:
            yield (seq,(sid,zlib.decompress(rstore[sid])))
            rstore[sid]=None
        elif mate:
            yield ((seq[0],reverseComplement(seq[1])),seq)
        else:
            yield (seq,(seq[0],reverseComplement(seq[1])))
            
    for sid,seq in rstore.items():
        if seq is not None:
            seq = zlib.decompress(seq)
            if mate:
                yield ((sid,reverseComplement(seq)),(sid,seq))
            else:
                yield ((sid,seq),(sid,reverseComplement(seq)))
                

   
    
        
def quantiles(stats,quantile):
    ls = list(stats.keys())
    ls.sort(reverse=True)    
    sums=[]
    s=0
    for l in ls:
        s+=stats[l]
        sums.append(s)
    qs = [float(x)/sums[-1] for x in sums]
    
    q=0
    
    try:
        while qs[q] < quantile:
            q+=1
    except IndexError:
        q = len(ls)-1
                        
    return ls[q]
        
        
def pairedEndLengthFilter(pairs,length):
    for p in pairs:
        if len(p[0][1]) >= length and len(p[1][1]) >= length:
            yield p        
    

def matePairs(pairs):
    for p in pairs:
        yield ((p[0][0],reverseComplement(p[0][1])),(p[1][0],reverseComplement(p[1][1])))        
    
       
def pairedEndCounter(pairs,n=-1,minlength=-1):
    
    i=0
    for p in pairs:
        if minlength==-1 or (len(p[0][1]) >= minlength and len(p[1][1]) >= minlength):
            yield p
            i+=1
            if i == n:
                break
            
    
        
def writeToFifo(pairs,forward,reverse,logger):
    logger.info("Forward tmp file : %s" % forward)
    logger.info("Reverse tmp file : %s" % reverse)
    i=0
    with open(forward,'w') as f, \
         open(reverse,'w') as r:
        for p in pairs:
            i+=1
            if not i % 1000000:
                logger.info('%d sequence pairs written' % i)
            if len(p[0][1]) > 0 and len(p[1][1]) > 0:
                print(formatFastq(p[0]),file=f)
                print(formatFastq(p[1]),file=r)
            
        

def run(config):

    logger  = config['orgasm']['logger']
    output  = config['orgasm']['indexfilename']
    forward = config['index']['forward']
    reverse = config['index']['reverse']
    fasta   = config['index']['fasta']
    nopipe  = config['index']['nopipe']
    
    if config['index']['reformat']:
        reformatOldIndex(config)
    else:
        if forward is None:
            logger.error('No sequence file specified')
            sys.exit(1)
    
    if nopipe:
        logger.info("Indexing in no pipe mode")
    
    fconvert = False
    rconvert = False
    
#     forward = uopen(forward)
#     
#     if reverse is not None:
#         reverse = uopen(reverse)
    
    if forward[-3:]=='.gz':
        logger.info('Forward file compressed by gzip')
        forward = ungzip(forward,nopipe)
         
    if forward[-4:]=='.bz2':
        logger.info('Forward file compressed by bzip2')
        forward = unbzip(forward,nopipe)
 
         
    if reverse is not None and reverse[-3:]=='.gz':
        logger.info('Reverse file compressed by gzip')
        reverse = ungzip(reverse,nopipe)
  
    if reverse is not None and reverse[-4:]=='.bz2':
        logger.info('Reverse file compressed by bzip2')
        reverse = unbzip(reverse,nopipe)
         
       
    cforward = readFastq(forward)
    creverse = readFastq(reverse) if reverse is not None else None
    pairs    = None
    
    if fasta or config['index']['ffasta']:
        logger.info('Forward file format is fasta')
        fconvert=True
        cforward = readFasta(forward)
        
    if fasta or config['index']['rfasta']:
        if creverse is not None:
            rconvert=True
            logger.info('Reverse file format is fasta')
            creverse = readFasta(reverse)
            
    if config['index']['estimate'] is not None:
        fconvert=True
        logger.info('Computing read length statistics for the forward file')
        stats,cforward = lengthStats(acgtCut(cforward))
        print(stats)
        quantile = quantiles(stats, config['index']['estimate'])
        if creverse is not None:
            logger.info('Computing read length statistics for the reverse file')
            rconvert=True
            stats,creverse = lengthStats(acgtCut(creverse))
            print(stats)
            quantile = min(quantiles(stats, config['index']['estimate']),quantile)
            
        logger.info('Read size considered for a quantile of %3.2f : %d',
                    config['index']['estimate'],
                    quantile)
        config['index']['length']=quantile

    if config['index']['single']:
        fconvert=True
        rconvert=True
        length = config['index']['length']
        if length is None:
            length=100
        logger.info('Simulate paired reads of %dbp' % length)
        pairs = singleToPairedEnd(cforward,length)
    else:
        if config['index']['checkpairs']:
            fconvert=True
            rconvert=True
            pairs = doubleToCheckedPairs(cforward,creverse,config['index']['mate'])
        elif fconvert or rconvert:
            pairs = doubleToPairedEnd(cforward,creverse,config['index']['checkids'])
            
            
    if config['index']['maxread'] is not None:
        logger.info('limit indexation to the first %d millions of reads' % config['index']['maxread'])
        
        if fconvert or rconvert : 
            if config['index']['length'] is None:
                pairs = pairedEndCounter(pairs,n=config['index']['maxread'])
            else:
                pairs = pairedEndCounter(pairs,n=config['index']['maxread'],
                                         minlength=config['index']['length'])
        
    if config['index']['mate']:
        pairs = matePairs(pairs)
        
        
    if not os.path.exists('%s.odx' % output ):
        os.makedirs('%s.odx' % output ) 
        
    command = ['orgasmi','-o','%s.odx/index'  % output]
    
    if config['index']['maxread'] is not None:
        command.append('-M')
        command.append(str(config['index']['maxread']))
        
    if config['index']['length'] is not None:
        command.append('-l')
        command.append(str(config['index']['length']))
        
    if fconvert or rconvert:
        forward = mktemp(prefix="forward-", dir=getTmpDir())
        atexit.register(postponerm(forward))
        
        if not nopipe:
            os.mkfifo(forward)
        
        reverse = mktemp(prefix="reverse-", dir=getTmpDir())
        atexit.register(postponerm(reverse))
        
        if not nopipe:
            os.mkfifo(reverse)
        
        
    command.append(forward)
    command.append(reverse)
    
    logger.info(" ".join(command))
    
    if fconvert or rconvert:
        if nopipe:
            logger.info("Writting transformed sequence files...")
            writeToFifo(pairs,forward,reverse,logger)
            logger.info("Done.")
            
            logger.info("Starting indexing...")
            logger.info(" ".join(command))
            os.system(" ".join(command)) 
        else:
            try:
                logger.info("Starting indexing...")
                process=Popen(command)
                writeToFifo(pairs,forward,reverse,logger)
                process.wait()
                logger.info('Done.')
            except BrokenPipeError:
                process.wait()
                logger.info('Done.')
                logger.warning("Maximum count of read indexed.")
                logger.warning("Indexing stopped but the index is usable.")
    else: 
        logger.info("Starting indexing...")
        logger.info(" ".join(command))
        os.system(" ".join(command)) 
    
        
    
    r=Index('%s.odx/index'  % output)
            
    logger.info('Count of indexed reads: %d' % len(r))  

              
