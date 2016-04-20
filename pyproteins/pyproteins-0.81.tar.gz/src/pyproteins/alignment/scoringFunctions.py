import numpy as np
import re

defaultAlphabet="ACDEFGHIKLMNPQRSTVWYX-"
# Should package these too !!
FILTER_LOCATION = { 'globular' : '/Users/guillaumelaunay/work/data/scoring/frosto_scores/all_globulars/AA_S6_C1_CD_1D',
                    'allAlphaTm' : '/Users/guillaumelaunay/work/data/scoring/frosto_scores/all_alpha_TM/FILTERS/AA_S6_C1_CD_1D'
}


class frosto1D(object):
    def __init__(self, filterLocation=FILTER_LOCATION):

        self.registred = { 'sse' : ['C', 'E', 'H'], 'burial' : ['b', 'e'] }
        self.globular = {}
        for sse in self.registred['sse']:
            trail = '_in.info'
            if sse == 'C': trail = '_out.info'
            for bs in self.registred['burial']:
                self.globular[sse + bs] = self._parseInfoFile(FILTER_LOCATION['globular'] + '/' + sse + bs + trail)

    def score(self, *kwargs):
        sseDef = False
        asaDef = False
        #aa1, sse1, aa2, sse2, asa1, asa2
        if not kwargs['aa1'] and not kwargs['aa2']:
            raise ValueError("No amino acid code")
        if kwargs['sse1'] and kwargs['sse2']:
            sseDef = True
            if kwargs['sse1'] not in self.registred['sse']:
                raise ValueError("Unknown sse code")
        if kwargs['asa1'] and kwargs['asa2']:
            asaDef = True
            if kwargs['asa1'] not in self.registred['burial']:
                raise ValueError("Unknown asa/burial code")

#        self.matrix[,]

    def _parseInfoFile(self, fileName):
        mBuffer = []
        alphabet = None
        matrix = None
        with open (fileName, "r") as f:
            for line in f:
                mBuffer.append(line.rstrip().split())
                if 'Alphabet' in line:
                    m = re.search(":[\s]+([\S]+)", line)
                    alphabet = m.groups(1)[0]

        return SubstitutionMatrix(alphabet, mBuffer[0:len(alphabet)])

#Defining alternative scores
#S3 stands for H/C/E
# We choose to discard gap from counts
    def setScore(self, *args):
        f = None

        if 'S3' in args:
            self.fScore = self.PepS3_scorer
            self.type = 'S3'
            self.alphabet = "ACDEFGHIKLMNPQRSTVWYX-"
            self.states = { 'H' : { 'counts' : None, 'sum' : None, 'score' : None },
                       'C' : { 'counts' : None, 'sum' : None, 'score' : None },
                       'E' : { 'counts' : None, 'sum' : None, 'score' : None }
                       }
            f = self.S3count

        total = 0
        for s in self.states:
            self.states[s]['counts'] = f(s)
            self.states[s]['sum'] = self.states[s]['counts'].sum()
            total += self.states[s]['sum']

        for s in self.states:
            self.states[s]['score'] = np.zeros(shape=[21,21], dtype=float)
            n_obs = self.states[s]['sum']
            if n_obs < 21 * 21:
                n_obs += 21 * 21
            for i in range(0, 21):
                for j in range(i, 21):
                    o_ij = self.states[s]['counts'][i, j] / n_obs
                    e_ij = (self.states[s]['counts'][i, :].sum() /n_obs) * (self.states[s]['counts'][:, j].sum() / n_obs)
                    if o_ij == 0.0:
                        o_ij = 1.0 / n_obs
                    if e_ij == 0.0:
                        e_ij = 1.0 / 21 * 21

                    self.states[s]['score'][i, j] = np.log10(o_ij / e_ij)
                    self.states[s]['score'][j, i] =  self.states[s]['score'][i, j]
                    self.states[s]['smat'] = SubstitutionMatrix(npMatrix = self.states[s]['score'], alphabet = self.alphabet)

# Foreach states
# 21x 21 matrix
# P_state(AAx->AAy)/ [P_state(AAx) * P_state(AAy) ]



    def _parseCountFile(self, fileName):
        total = 0
        m = []
        with open (fileName, "r") as f:
            for line in f:
                l = line.split()
                if not l:
                    break

                total += int(l.pop())
                m.append(l)
        return np.array([ r[0:21] for r in m[0:21] ], dtype=int)



    def S3count(self, ss2Letter):
        inputs = [ss2Letter + 'b_in.counts', ss2Letter + 'b_out.counts',
                        ss2Letter + 'e_in.counts', ss2Letter + 'e_out.counts']
        m = np.zeros(shape=[21, 21])
        for f in inputs:
            m += self._parseCountFile(FILTER_LOCATION['globular'] + "/" + f)
        return m

    def PepS3_scorer(self, e1, e2):
        sc1 = self.states[e1.ss2]['smat'][e1.aa, e2.aa]
        sc2 = self.states[e2.ss2]['smat'][e2.aa, e1.aa]
        return (sc1 + sc2) / 2

def unwrap_Needle(arg, **kwarg):
    return C.f(*arg, **kwarg)

class Needle(object): #pairwise alignment btwn sequences
    def __init__(self, alphabet=defaultAlphabet):
        if not alphabet:
            raise ValueError("You must provide an amino-acid alphabet specifying the ordering of the frequency vectors")
    # must provide as mentioned in nw_custom, element iterator and elements pair scorer
        self._scoremat = Blosum62()
    def fScore(self, position1, position2):
        #print 'dist:' + position1.aa + ' ' + position2.aa
        #if position1.alphabet != position2.alphabet:
        #    raise TypeError ('Needle applied to different alphabet frequency vectors')
        return self._scoremat[position1.aa, position2.aa]

class PWS(object): # classical PWMATRIX making use of Blosum 62
    def __init__(self, alphabet=None):
        if not alphabet:
            raise ValueError("You must provide an amino-acid alphabet specifying the ordering of the frequency vectors")
    # must provide as mentioned in nw_custom, element iterator and elements pair scorer
        self._scoremat = Blosum62()
    def fScore(self, freqPosition1, freqPosition2):
        if freqPosition1.alphabet != freqPosition2.alphabet:
            raise TypeError ('PWS applied to different alphabet frequency vectors')
        sub_score = 0

        for i in range(0, len(freqPosition1)):
            aa_i = freqPosition1.alphabet[i]
            fq_i = freqPosition1[i]
            if aa_i == '-':
                continue
            for j in range(0, len(freqPosition2)):
                aa_j = freqPosition2.alphabet[j]
                fq_j = freqPosition2[j]
                if aa_j == '-':
                    continue
                sub_score += self._scoremat[aa_i, aa_j] * fq_i * fq_j
        return sub_score
    #def matchScorer(self, e1, e2): #defines identity
    #    pass


class SubstitutionMatrix(object):
    def __init__(self, alphabet, matrix=None, npMatrix=None):
        if matrix:
            self.matrix = np.array(matrix, dtype=float)
        elif npMatrix.any():
            self.matrix = npMatrix
        self.alphabet = alphabet

    def __getitem__(self, tup):
        y, x = tup

        if y not in self.alphabet:
            raise ValueError("\"" + y + "\" is not part of alphabet")

        if x not in self.alphabet:
            raise ValueError("\"" + x + "\" is not part of alphabet")
        #print "-->" + self.alphabet
        #if not x['code'] or not y['code']:
        #    raise TypeError("no amino acid code provided")

        return self.matrix[self.alphabet.index(y), self.alphabet.index(x)]



class Blosum62(SubstitutionMatrix):
    def __init__(self):
#  Matrix made by matblas from blosum62.iij
#  * column uses minimum score
#  BLOSUM Clustered Scoring Matrix in 1/2 Bit Units
#  Blocks Database = /data/blocks_5.0/blocks.dat
#  Cluster Percentage: >= 62
#  Entropy =   0.6979, Expected =  -0.5209
        alphabet = 'ARNDCQEGHILKMFPSTWYVBZX*'

        matrix = [
        [4, -1, -2, -2, 0, -1, -1, 0, -2, -1, -1, -1, -1, -2, -1, 1, 0, -3, -2, 0, -2, -1, 0, -4],
        [1, 5, 0, -2, -3, 1, 0, -2, 0, -3, -2, 2, -1, -3, -2, -1, -1, -3, -2, -3, -1, 0, -1, -4],
        [2, 0, 6, 1, -3, 0, 0, 0, 1, -3, -3, 0, -2, -3, -2, 1, 0, -4, -2, -3, 3, 0, -1, -4],
        [2, -2, 1, 6, -3, 0, 2, -1, -1, -3, -4, -1, -3, -3, -1, 0, -1, -4, -3, -3, 4, 1, -1, -4],
        [0, -3, -3, -3, 9, -3, -4, -3, -3, -1, -1, -3, -1, -2, -3, -1, -1, -2, -2, -1, -3, -3, -2, -4],
        [1, 1, 0, 0, -3, 5, 2, -2, 0, -3, -2, 1, 0, -3, -1, 0, -1, -2, -1, -2, 0, 3, -1, -4],
        [1, 0, 0, 2, -4, 2, 5, -2, 0, -3, -3, 1, -2, -3, -1, 0, -1, -3, -2, -2, 1, 4, -1, -4],
        [0, -2, 0, -1, -3, -2, -2, 6, -2, -4, -4, -2, -3, -3, -2, 0, -2, -2, -3, -3, -1, -2, -1, -4],
        [2, 0, 1, -1, -3, 0, 0, -2, 8, -3, -3, -1, -2, -1, -2, -1, -2, -2, 2, -3, 0, 0, -1, -4],
        [1, -3, -3, -3, -1, -3, -3, -4, -3, 4, 2, -3, 1, 0, -3, -2, -1, -3, -1, 3, -3, -3, -1, -4],
        [1, -2, -3, -4, -1, -2, -3, -4, -3, 2, 4, -2, 2, 0, -3, -2, -1, -2, -1, 1, -4, -3, -1, -4],
        [1, 2, 0, -1, -3, 1, 1, -2, -1, -3, -2, 5, -1, -3, -1, 0, -1, -3, -2, -2, 0, 1, -1, -4],
        [1, -1, -2, -3, -1, 0, -2, -3, -2, 1, 2, -1, 5, 0, -2, -1, -1, -1, -1, 1, -3, -1, -1, -4],
        [2, -3, -3, -3, -2, -3, -3, -3, -1, 0, 0, -3, 0, 6, -4, -2, -2, 1, 3, -1, -3, -3, -1, -4],
        [1, -2, -2, -1, -3, -1, -1, -2, -2, -3, -3, -1, -2, -4, 7, -1, -1, -4, -3, -2, -2, -1, -2, -4],
        [1, -1, 1, 0, -1, 0, 0, 0, -1, -2, -2, 0, -1, -2, -1, 4, 1, -3, -2, -2, 0, 0, 0, -4],
        [0, -1, 0, -1, -1, -1, -1, -2, -2, -1, -1, -1, -1, -2, -1, 1, 5, -2, -2, 0, -1, -1, 0, -4],
        [3, -3, -4, -4, -2, -2, -3, -2, -2, -3, -2, -3, -1, 1, -4, -3, -2, 11, 2, -3, -4, -3, -2, -4],
        [2, -2, -2, -3, -2, -1, -2, -3, 2, -1, -1, -2, -1, 3, -3, -2, -2, 2, 7, -1, -3, -2, -1, -4],
        [0, -3, -3, -3, -1, -2, -2, -3, -3, 3, 1, -2, 1, -1, -2, -2, 0, -3, -1, 4, -3, -2, -1, -4],
        [2, -1, 3, 4, -3, 0, 1, -1, 0, -3, -4, 0, -3, -3, -2, 0, -1, -4, -3, -3, 4, 1, -1, -4],
        [1, 0, 0, 1, -3, 3, 4, -2, 0, -3, -3, 1, -1, -3, -1, 0, -1, -3, -2, -2, 1, 4, -1, -4],
        [0, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2, 0, 0, -2, -1, -1, -1, -1, -1, -4],
        [4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, 1]
        ]
        SubstitutionMatrix.__init__(self, alphabet, matrix)
