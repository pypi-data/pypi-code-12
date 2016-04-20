import pprint
from Bio import AlignIO
import re
import sys
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
import json
from copy import copy, deepcopy

import pyproteins.alignment.nw_custom
import pyproteins.sequence.peptide
import pyproteins.alignment.scoringFunctions

import pathos.multiprocessing as mp


pp = pprint.PrettyPrinter(indent=4)


class initError(Exception):
    pass

class RulerError(Exception):
    def __init__(self, ruler):
        self.ruler = ruler

class SliceError(Exception):
    def __init__(self, sliceExpression):
        self.sliceExpression = sliceExpression

class AlignmentError(Exception):
    def __init__(self, nSeq):
        self.nSeq = nSeq

class AlignmentLengthError(AlignmentError):
    def __init__(self, base, nSeq, nLen):
        AlignmentError.__init__(self, nSeq)
        self.nSeq = nSeq
        self.nLen = nLen

class AlignmentTypeError(AlignmentError):
    def __init__(self, nSeq, nPos, char):
        AlignmentError.__init__(self, nSeq)
        self.nPos = nPos


aaCoherce = {
    'A':'A',
    'C':'C',
    'D':'D',
    'E':'E',
    'F':'F',
    'G':'G',
    'H':'H',
    'I':'I',
    'K':'K',
    'L':'L',
    'M':'M',
    'N':'N',
    'P':'P',
    'Q':'Q',
    'R':'R',
    'S':'S',
    'T':'T',
    'V':'V',
    'W':'W',
    'Y':'Y',
    'Z': 'E',
    'B': 'D',
    'J': 'L',
    'X': 'A',
    ' ': '-',
    '-': '-'
}


class Position():  ## Used for NW and custom scoring interface
    def __init__(self, e):
        self.aa = e['aa'].upper()
        self._ss2 = e['ss2']
        self.burial = e["burial"]
    def __repr__(self):
        return self.aa
    def __eq__(i, j):
        if i.aa != j.aa:
            return False
        if i._ss2 and j._ss2:
            if i._ss2 != j._ss2:
                return False
        elif i._ss2 and not j._ss2:
            return False
        elif j._ss2 and not i._ss2:
            return False

        if i.burial and j.burial:
            if i.burial != j.burial:
                return False
        elif i.burial and not j.burial:
            return False
        elif j.burial and not i.burial:
            return False

        return True
    @property # emulate str(self.ss2)
    def ss2(self):
        if self._ss2:
            return self._ss2
        return ' '

class VectorFreq(): # this class provides the interface w/ the nw custom scoring
    def __init__(self, msaObject, seqNumRef=0):
        self.refSeq = msaObject[seqNumRef]['sequence']
        skippedColumns = [i for i,j in enumerate(self.refSeq) if j == '-']
        self.__hookedMsa__ = msaObject
        freq = [[ col[aa] / float(msaObject.shape()[0]) for aa in msaObject.alphabet ] for icol, col in enumerate(msaObject.frequency) if icol not in skippedColumns ]
        self.refSeq = self.refSeq.replace('-','', len(self.refSeq))
        self.data = [freqPosition({'aa' : self.refSeq[i], 'ss2' : None, 'burial' : None, 'f' : freq[i] }, self.__hookedMsa__) for i in range(0, len(freq))]

    def homogenize(self):
        def fn(fPos):
            i = fPos.alphabet.index(fPos.aa)
            fPos.freq = [ 1.0 if i == j else 0.0 for j,f in enumerate(fPos.freq) ]
            return fPos
        self.data = [fn(fPos) for fPos in self.data]


    def __repr__(self):
        return str(self.refSeq)

    def __getitem__(self, i):
        if i < 0:
            raise ValueError("minimal amino-acid number is 1")
        return self.data[i]

    @property
    def alphabet(self):
        return self.__hookedMsa__.alphabet

    @property
    def id(self):
        return self.__hookedMsa__.id

    def __len__(self):
        return len(self.refSeq)

    @property
    def hasSse(self):
        return False

class freqPosition(Position):  ## Used for NW and custom scoring interface
    def __init__(self, e, __hookedMsa__):
        Position.__init__(self, e)
        self.freq = e['f']
        self.__hookedMsa__ =  __hookedMsa__
    #def __repr__
    #def __eq__(i, j):
    def __len__(self):
        return len(self.freq)
    @property
    def alphabet(self):
        return self.__hookedMsa__.alphabet
    def __getitem__(self, k):
        return self.freq[k]

#
#
#
# will return a vector of msaRef column numbers, with a value for the
# eventual corresponding column number in msaShrink
#
# TODO: wrap&use hmmr to align the two msa by their profiles
#
#

def map(msaRef, msaShrink):
    import scoringFunctions
    import nw_custom
    PWS=scoringFunctions.PWS(alphabet=msaRef.alphabet)
    nw = nw_custom.nw(matchScorer=PWS.fScore)
    aln = nw.align(msaRef.vectors, msaShrink.vectors)

    return aln

# We need to fill a matrix of distances sized to the query msa

#def cloneAlphaDist():



class MsaBean():
    def __init__(self, matrix, header, backtrack=None):
        self.header = header
        self.matrix = [ [aaCoherce[x] for x in r] for r in matrix ]
        self.backtrack = backtrack
        # HARD REPLACE ALL X instances by A


class Msa(object):  # HARD REPLACE ALL X instances by A

    def vectors(self, seqNumRef=0):
        return VectorFreq(self, seqNumRef=0)


    def _scan_parallel_joblib(self, queryPeptide, n):
        Needle=scoringFunctions.Needle(alphabet=self.alphabet)
        nw_scan = nw_custom.nw(gapOpen=-10, gapExtend=-0.5, matchScorer=Needle.fScore)
        mPool = mp.Pool(n)
        inputs = [ [queryPeptide, p] for p in self.peptideArray ]
        hits = mPool.map(nw_scan.mp_align, inputs)
        return [{ 'sim' : float(ali.simPct) ,'ali': ali} for ali in hits]

    def scan(self, queryPeptide=None, _num_worker=1, recordLookup=False):
        #print "Scaning a " + str(self.nSeq) + " sequences msa w/ " + str(_num_worker) + " threads"
        if _num_worker > 1:
            hit_buffer=self._scan_parallel_joblib(queryPeptide, _num_worker)
        else:
            hit_buffer = []
            Needle=scoringFunctions.Needle(alphabet=self.alphabet)
            nw_scan = nw_custom.nw(gapOpen=-10, gapExtend=-0.5, matchScorer=Needle.fScore)
            for i in range(0, self.nSeq):
                ali = nw_scan.align(queryPeptide, self.getPept(i))
                hit_buffer.append({ 'sim' : float(ali.simPct) ,'ali': ali})


        return sorted(hit_buffer, key=lambda k: k['sim'])

    @property
    def peptideArray(self):
        for i in range (self.nSeq):
            p = self.getPept(i)
            yield(p)

    def getPept(self, x):
        hits = self.recordLookup(num=x)
        rec = hits.pop(0)
        return Peptide.Entry(id=rec['header'], seq=rec['sequence'])

    def __init__(self, fileName = None, msaBean = None, alphabet = "ACDEFGHIKLMNPQRSTVWY-", backtrack = None, jsBeanFile = None, id=None):
        self.alphabet = alphabet
        self.backtrack = backtrack
        self.id = id if id else "id_default_msa"
        if fileName:
            fType = None
            if fileName.endswith(".aln"): fType = "clustal"
            else : fType = "fasta"
            self.alignment = AlignIO.read(open(fileName), fType) # fasta
            self.asMatrix = [[ aaCoherce[aa] for aa in list(record.seq) ] for record in self.alignment]
            self.headers = [record.id for record in self.alignment]
           # print dir(self.alignment)
           # print dir (self.asMatrix)
           # print self.alignment.annotations
        elif msaBean:
            self.asMatrix = msaBean.matrix
            self.headers = msaBean.header
            self.backtrack = msaBean.backtrack
            #self.alignment = [seq for seq in msaBean.matrix]
            # same for headers
        elif jsBeanFile:
            with open(jsBeanFile) as json_file:
                json_data = json.load(json_file)
            self.asMatrix = json_data['matrix']
            self.headers = json_data['headers']
            self.backtrack = json_data['backtrack']

        else:
            raise initError("You must specify a bean or a mfasta file")

        self.nSeq = len(self.asMatrix)
        self.length = len(self.asMatrix[0])
        self.frequency = [{c : 0 for c in list(alphabet)} for nCol in range(self.length)]


        for oRow in enumerate(self.asMatrix):

            nRow = oRow[0]
            row = oRow[1]
            try:
                if (len(row) != self.length):
                    raise AlignmentLengthError(nSeq = nRow, nLen = len(row), base = self.length)
                for oCell in enumerate(row):
                    nCol = oCell[0]
                    char = oCell[1]
                    if not re.search(char, alphabet):
                        print "unknown character" + char
                        raise AlignmentTypeError(nSeq = nRow, nPos = nCol, char = char)
                        #sys.exit()
                    else:
                        self.frequency[nCol][char] += 1

            except AlignmentLengthError as e:
                print 'Wrong'
                print "sequence length " + str(e.nLen) + " do not match at " + str(e.nSeq) + " (base length is " + str(e.nLen) + ")"
                sys.exit(0)
            except AlignmentTypeError as e:
                print "unknown character \'" + str(e.char) + "\' at position " + str(e.nPos) + " in sequence " + str(e.nSeq)
                sys.exit(0)

    def __iter__(self):
        for i in range(0, self.nSeq):
            if self.backtrack:
                yield {'header' : self.headers[i], 'seq' : self.asMatrix[i], 'back' : self.backtrack[i]}
            else:
                yield {'header' : self.headers[i], 'seq' : self.asMatrix[i] }
    def set_id(self, id):
        self.id = id

    def setHeader(self, i, string):
        self.headers[i] = string

    def sliceTo(self, litteral=None, columnSlice='*', recordSlice='*'):

        def _parse(expr):
            columnSlice='*'
            recordSlice='*'
            array = expr.split(";") # ['c:<10', 's:[1:5, 7:8]']
            try:
                for exp in array:
                    if exp.startswith('c:'):
                        columnSlice = exp.replace("c:", '', 1)
                    elif exp.startswith('s:'):
                        recordSlice = exp.replace("s:", '', 1)
                    else:
                        raise SliceError
            except(SliceError) as e:
                print "Invalid slice expression \'" + litteral + "\'"

            return {
                'column' : columnSlice,
                'record' : recordSlice
            }

        def _factorize (ruler):
            ruleOut = []
            curUp = ruler[0]['up']
            curLo = ruler[0]['lo']
            for ind, bracket in enumerate(ruler):
                if ind == 0:
                    continue
                if bracket['lo'] == (curUp + 1):
                  #  print "FUSE " + str(curUp) +" to " + str(bracket['up'])
                    curUp = bracket['up']
                else:
             #       print ""
                    ruleOut.append({'lo' : curLo, 'up' : curUp})
                    curLo = bracket['lo']
                    curUp = bracket['up']

            ruleOut.append({'lo' : curLo, 'up' : curUp})

            #print "factorized ruler " + str(ruleOut)
            return ruleOut
                #{ 'lo' : int(reg.split(':')[0]), 'up'

        def _setSlicer(sliceExpression, nMax):
            ruler = None
            if isinstance(sliceExpression, list):
                ruler = [ { 'lo' : int(reg.split(':')[0]), 'up' : int(reg.split(':')[1]) } for reg in sliceExpression ]
            elif isinstance(sliceExpression, basestring):
                if sliceExpression == "*":
                    ruler = [{'lo' : 0, 'up' : nMax - 1 }]
                else:
                    try:
                        m = re.search("(<=|<|\?|>|>=){1}(\d+)", sliceExpression)
                        if not m:
                            raise SliceError(sliceExpression)
                        else:
                            if not m.groups()[1]:
                                raise SliceError(sliceExpression)
                        #print m.groups()
                            if m.groups()[0] == "<=":
                                ruler = [{'lo' : 0, 'up' : int(m.groups()[1])}]
                            elif m.groups()[0] == "<":
                                ruler = [{'lo' : 0, 'up' : int(m.groups()[1]) - 1}]
                            elif m.groups()[0] == ">=":
                                ruler = [{'lo' : int(m.groups()[1]), 'up' : nMax - 1}]
                            elif m.groups()[0] == ">":
                                ruler = [{'lo' : int(m.groups()[1]) + 1, 'up' : nMax - 1}]
                            else:
                                raise SliceError(sliceExpression)
                    except SliceError as e:
                        print "Invalid slice expression \'" + str(e.sliceExpression) + "\'"
                        print "must be \"*\" or \">=|>|<|<=someNumber\""
                        sys.exit(0)
            ruleOut = _factorize(ruler)
            return ruleOut

        def _isRuledIn(nSeq, ruler):
            try:
                for interval in ruler:
                    if nSeq >= interval['lo'] and nSeq <= interval['up']:
                        return True
            except(TypeError):
                raise RulerError(ruler=ruler)
            return False

        if litteral:
            data = _parse(litteral)
            columnSlice = data['column']
            recordSlice = data['record']

        seqRuler = _setSlicer(recordSlice, self.nSeq)
        try:
            matrixTmp = [ x for ind, x in enumerate(self.asMatrix) if _isRuledIn(ind, seqRuler)]
            header = [ x for ind, x in enumerate(self.headers) if _isRuledIn(ind, seqRuler)]
        except(RulerError) as e:
            print "Invalid ruler to splice records of Msa"
            print e.ruler
            sys.exit(0)
        colRuler = _setSlicer(columnSlice, self.length)
        try:
            matrix = [[ x for ind, x in enumerate(seq) if _isRuledIn(ind, colRuler)] for seq in matrixTmp]
        except(RulerError) as e:
            print "Invalid ruler to splice columns of Msa"
            print e.ruler
            sys.exit(0)

# Try to keep track of original column numbering in remaining sequences
        if self.backtrack: # splcie existing
            backtrack = self.backtrack # just get ref, matrix wont be modified
            backtrackTmp = [ x for ind, x in enumerate(backtrack) if _isRuledIn(ind, seqRuler)]
            backtrackNew = [[ x for ind, x in enumerate(seq) if _isRuledIn(ind, colRuler)] for seq in backtrackTmp]

        else : # Create it from scarch
            backtrackNew = [];
            n = 0;
            for seq in matrixTmp:
                seqPos = -1
                backtrackNew.append([]);
                for ind,x in enumerate(seq):
                    if x != "-":
                        seqPos = seqPos + 1
                    if _isRuledIn(ind, colRuler):
                    #print str(ind) + "is ruled in"
                        if x == "-":
                            backtrackNew[n].append(-1)
                        else:
                            backtrackNew[n].append(seqPos)
                n = n + 1;

        #print backtrackNew



        #for ind, x in enumerate(self.backtrack):
        #    print "sequence %5d %s" % (ind, x)

        #print backtrackNew
        bean = MsaBean(header = header, matrix = matrix, backtrack = backtrackNew)
       # newMsa = Msa(msaBean = bean, backtrack = self.backtrack)
        newMsa = Msa(msaBean = bean)
        #print newMsa.backtrack
        return newMsa

    def gapPurge (self, gapRatio = 0.5):
        nGap = float(self.nSeq) < gapRatio
        sliceList = [ str(eO[0]) + ':' + str(eO[0]) for eO in enumerate(self.frequency) if float(eO[1]['-']) / float(self.nSeq) <= float(gapRatio)]
        print "keeping " + str(len(sliceList)) + "/" + str(self.length) + " columns w/ gap ratio < " + gapRatio
        #print str(sliceList)

        delCol = []
        for eO in enumerate(self.frequency):
            if float(eO[1]['-']) / float(self.nSeq) > float(gapRatio):
                delCol.append(eO)

        print "Total number of del columns " + str(len(delCol))


        msaObject = self.sliceTo(columnSlice = sliceList)
        return msaObject

    def __repr__(self):

        header = "Alignment dimensions = " + str(self.nSeq) + " sequences, " + str(self.length) + " columns\n"
        # pretty print the frequencies
        freqAsString = "nCol" + re.sub("(?P<name>\w{1})", "  " + '\g<name>' + "  ", self.alphabet) + "\n"
        for iCol in range (self.length):
            freqAsString += "  "
            for iChar in list (self.alphabet):
                freqAsString += "%5s" % (self.frequency[iCol][iChar])
            freqAsString += "\n"
        return  header + freqAsString
        #return str(self.asMatrix)

    def fastaDump(self, outputFile=None):
        if (outputFile):
            f = open(outputFile,'w')
            f.write(self.format('fasta'))
            f.close()
        else :
            return self.format('fasta')

    def asDict(self):
        backtrack = ''
        if self.backtrack:
            backtrack = self.backtrack

        return {
            'matrix' : self.asMatrix,
            'headers' : self.headers,
            'backtrack' : backtrack,
            'frequency' : self.frequency
        }

    def asJSON(self):
        dic = self.asDict()
        jsonString = json.JSONEncoder().encode(dic)
        return jsonString

    def shape(self) :
        return [self.nSeq, self.length]

    # retrieve a sequence in the msa, by index or regular expression
    # gap will be striped
    def recordLookup(self, num=None, regExp=None):
        def _strip(r):
            d = copy.deepcopy(r)
            if 'seq' in d:
                d['sequence'] = d['seq']
                d.pop("seq", None)
            string = ''.join(d['sequence'])
            d['sequence'] = string.replace('-', '', len(string))
            return d

        if num or num == 0:
            d = self[num]
            return [_strip(d)]

        if not num and not regExp:
            return [_strip(d) for d in self]

        hits = []
        if regExp:
            for r in self:
                x = _strip(r)
                m = re.search(regExp, x['sequence'])
                if m:
                    #print m
                    hits.append(x)
            return hits

    def __getitem__(self, k):
        return {'header' : self.headers[k], 'sequence' : ''.join(self.asMatrix[k]) }

    def format(self, formatType):
        if not formatType is 'fasta':
            print "unknown format Type \'" + str(formatType) + "\'"
            sys.exit()

        msaAsString = ''
        for eO in enumerate(self.asMatrix):
            record = SeqRecord(Seq(''.join(eO[1]),IUPAC.protein),
                            id=self.headers[eO[0]], name="", description="")
            msaAsString += record.format("fasta")

        return msaAsString


'''
    def _scan_parallel(self, n):
        num_worker_threads = n
        hit_buffer = []
        Needle=scoringFunctions.Needle(alphabet=self.alphabet)
        def worker():
            while True:
                i_num = q.get()
                pept = self.getPept(i_num)

                nw_scan = nw_custom.nw(gapOpen=-10, gapExtend=-0.5, matchScorer=Needle.fScore)
                ali = nw_scan.align(queryPeptide, pept)
                hit_buffer.append({ 'sim' : float(ali.simPct) ,'ali': ali, 'num' : i_num})
                q.task_done()

        q = Queue()
        for i in range(num_worker_threads):
            t = Thread(target=worker)
            t.daemon = True
            t.start()

        for i in range(0, self.nSeq):
            q.put(i)


        print '*** Main thread waiting ' + str(q.qsize())
        q.join()
        #print '*** Done'
        return hit_buffer
'''

