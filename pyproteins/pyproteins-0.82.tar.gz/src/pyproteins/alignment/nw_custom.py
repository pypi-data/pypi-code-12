import numpy as np
import StringIO
import json
import re
import scoringFunctions
#import numba #--> speed up vector matrix walks
#from numba import jit
# entities must have a getitem
# scorer must return float given a pair of entity item

def x_static_dp(e1, e2, alphabet):
#    print ">>>" + str(e1)
#    print "<<<" + str(e2)

    Needle_X = scoringFunctions.Needle(alphabet=alphabet)
    return True

 #   nw_scan = nw_custom.nw(gapOpen=-10, gapExtend=-0.5, matchScorer=Needle.fScore)
 #   ali = ali.align(e1,e2)
 #   return { 'sim' : float(ali.simPct) ,'ali': ali}

def p_static_dp(**kwargs):
    print kwargs['e2']

    #print e2
    #ali = _static_dp(kwargs['e1'], kwargs['e2'], kwargs['go'], kwargs['ge']) # scoringFunc.fScore
    #if kwargs['picklePack']:
    #    fscore = _unpickle_method()
    #if picklePack in
    return True



def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if func_name.startswith('__') and not func_name.endswith('__'):
        cls_name = cls.__name__.lstrip('_')
    if cls_name: func_name = '_' + cls_name + func_name
    return _unpickle_method, (func_name, obj, cls)


#def nw_custom.picklePack(alphabet):
#    Needle=scoringFunctions.Needle(alphabet=alphabet)
#    fn = _pickle_method()
#    return {'go' : -10, 'ge' : -0.5, 'fScore' : Needle.fScore }
    #nw_scan = nw_custom.nw(gapOpen=-10, gapExtend=-0.5, matchScorer=Needle.fScore)


#@jit
def _static_dp(entityOne, entityTwo, go, ge, matchCost):

#    if '_hook' in kwargs:
#        go = kwargs['_hook'].go
#        ge = kwargs['_hook'].ge
#        matchCost = _hook.matchCost
#    elif kwargs['go'] and kwargs['ge'] and kwargs['scorer']:
#        go = kwargs['go']
#        ge = kwargs['ge']
#        matchCost = kwargs['scorer']
 #   else:
 #       raise "Cant run DP"

    def _vic (path_mat, score_mat, go, ge, i, j):
        if path_mat[i][j - 1] != "\\" :
            return score_mat[i][j - 1] + ge;
        else :
            return score_mat[i][j - 1] + go;
    def _hic (path_mat, score_mat, go, ge, i, j):
        if path_mat[i - 1][j] != '\\':
            return score_mat[i - 1][j] + ge;
        else :
            return score_mat[i - 1][j] + go;


    shape = [len(entityOne) + 1, len(entityTwo) + 1]
    wordOne = str(entityOne)
    wordTwo = str(entityTwo)

    score_mat = np.zeros(shape=shape)
    path_mat = np.full(shape=shape, fill_value='', dtype=str)
    path_mat[0][0] = '*'

        # Gaps at the beginning of the sequences
    score_mat[0][1] = go
    for i in range(1, shape[0]):
        score_mat[i][0] = score_mat[i - 1][0] + ge
        path_mat[i][0] = '|'

    for j in range(1, shape[1]):
        score_mat[0][j] = score_mat[0][j - 1] + ge
        path_mat[0][j] = '-'
  #The matrix
    for i in range(1, shape[0]):
        for j in range(1, shape[1]):
            ivc = _vic(path_mat, score_mat, go, ge, i, j)
            ihc = _hic(path_mat, score_mat, go, ge, i, j)
            ali = matchCost(entityOne[i - 1], entityTwo[j - 1]) + score_mat[i - 1][j - 1]
            if ali >= ivc and ali >= ihc:
                path_mat[i][j] = '\\'
                score_mat[i][j] = ali
            elif ihc >= ivc:
                path_mat[i][j] = '|'
                score_mat[i][j] = ihc
            else :
                path_mat[i][j] = '-'
                score_mat[i][j] = ivc

 # Gaps at the end of the sequences */
    j = shape[1] - 1;
    for i in range(1, shape[0]):
        ivc = score_mat[i - 1][j] + ge
        if path_mat[i - 1][j] == '\\':
            ivc += ge
        if ivc > score_mat[i][j]:
            path_mat[i][j] = '|'
            score_mat[i][j] = ivc

    i = shape[0] - 1
    for j in range(1, shape[1]):
        ihc = score_mat[i][j - 1] + ge
        if path_mat[i][j - 1] == '\\':
            ihc += go
        if ihc > score_mat[i][j]:
            path_mat[i][j] = '-'
            score_mat[i][j] = ihc


    #self.score_mat = score_mat
    #self.path_mat = path_mat
    #self.shape = shape


    return Alignment(e1=entityOne, e2=entityTwo, score_mat=score_mat, path_mat=path_mat, matchCost=matchCost)




#entityOne = ["CHAPEAU"]
#entityTwo = ["CHAPITEAU"]

def _matchScorer(e1, e2):
    if e1 == e2:
        return 1
    return -1

class viewer(object):
    def __init__(self, _hookAlignment):
        self._hook_ = _hookAlignment
        self.score_mat = self._hook_.score_mat
        self.path_mat = self._hook_.path_mat
        self.w1 = list(self._hook_.e1.seq)
        self.w2 = list(self._hook_.e2.seq)
        #self.w1 = [ str(self._hook_.e1[i]) for i,c in enumerate(self._hook_.e1) ]
        #self.w2 = [ str(self._hook_.e2[i]) for i,c in enumerate(self._hook_.e2) ]

    def _repr_html_(self):
        Score_htmlContent = '<table><tr><td></td><td></td>'
        BackTrace_htmlContent = '<table><tr><td></td><td></td>'

        for c in self.w2:
            Score_htmlContent += '<td>' + str(c) + '</td>'
            BackTrace_htmlContent += '<td>' + str(c) + '</td>'

       # BackTrace_htmlContent = '<table><tr><td></td>' + str(['<td>' + str(c) + '</td>' for c in self.w2]) + '</tr>'
        for i, row in enumerate(self.score_mat):
            pre = '<td></td>' if i ==0 else '<td>' +  str(self.w1[i-1]) +'</td>'
            Score_htmlContent += '<tr>' + pre
            BackTrace_htmlContent += '<tr>' + pre
            for j, cell in enumerate(row):
                Score_htmlContent += '<td>' + str(cell) + '</td>'
                BackTrace_htmlContent += '<td>' + str(self.path_mat[i][j]) + '</td>'
            Score_htmlContent += '</tr>'
            BackTrace_htmlContent += '</tr>'
        Score_htmlContent += '</table>'
        BackTrace_htmlContent += '</table>'
        return Score_htmlContent + BackTrace_htmlContent

class nw(object):
    def __repr__(self):
        string1 = "Score matrix:\n              "
        string2 = "Path matrix:\n              "
        if not self.wordTwo:
            return "No alignment"

        for e in self.wordTwo:
            string1 += "%7s" % (str(e))
            string2 += "%7s" % (str(e))
        string1 += "\n"
        string2 += "\n"

        for i in range(0, self.shape[0]):
            if i > 0:
                string1 += "%7s" % (str(self.wordOne[i - 1]))
                string2 += "%7s" % (str(self.wordOne[i - 1]))
            else:
                string1 += "       "
                string2 += "       "
            for j in range(0, self.shape[1]):
                string1 += "%7s" % (str(self.score_mat[i][j]))
                string2 += "%7s" % (str(self.path_mat[i][j]))
            string1 += "\n"
            string2 += "\n"
        return string1 + "\n" + string2

    def __init__(self, gapOpen=-1.0, gapExtend=-1.0, matchScorer=_matchScorer):
        self.go = gapOpen
        self.ge = gapExtend
        self.matchCost = matchScorer
        self.wordOne = None
        self.wordTwo = None

    def vertiInsertionCost (self, i, j):
            if self.path_mat[i][j - 1] != "\\" :
                return self.score_mat[i][j - 1] + self.ge;
            else :
                return self.score_mat[i][j - 1] + self.go;
    def horizInsertionCost (self, i, j):
            if self.path_mat[i - 1][j] != '\\':
                return self.score_mat[i - 1][j] + self.ge;
            else :
                return self.score_mat[i - 1][j] + self.go;


    def mp_align(self, arg): # mp map seems to accept a single list as argument
                             # see http://stackoverflow.com/questions/19984152/what-can-multiprocessing-and-dill-do-together
        ali = self.align(arg[0], arg[1])
        return ali
# jit decorator tells Numba to compile this function.
    #@jit
    def align(self, entityOne, entityTwo):
        def _vic (path_mat, score_mat, go, ge, i, j):
            if path_mat[i][j - 1] != "\\" :
                return score_mat[i][j - 1] + ge;
            else :
                return score_mat[i][j - 1] + go;
        def _hic (path_mat, score_mat, go, ge, i, j):
            if path_mat[i - 1][j] != '\\':
                return score_mat[i - 1][j] + ge;
            else :
                return score_mat[i - 1][j] + go;

        matchCost = self.matchCost

        shape = [len(entityOne) + 1, len(entityTwo) + 1]
        wordOne = str(entityOne)
        wordTwo = str(entityTwo)
        go = self.go
        ge = self.ge
        score_mat = np.zeros(shape=shape)
        path_mat = np.full(shape=shape, fill_value='', dtype=str)
        path_mat[0][0] = '*'

        # Gaps at the beginning of the sequences
        score_mat[0][1] = go
        for i in range(1, shape[0]):
            score_mat[i][0] = score_mat[i - 1][0] + ge
            path_mat[i][0] = '|'

        for j in range(1, shape[1]):
            score_mat[0][j] = score_mat[0][j - 1] + ge
            path_mat[0][j] = '-'
  #The matrix
        for i in range(1, shape[0]):
            for j in range(1, shape[1]):
                ivc = _vic(path_mat, score_mat, go, ge, i, j)
                ihc = _hic(path_mat, score_mat, go, ge, i, j)
                ali = matchCost(entityOne[i - 1], entityTwo[j - 1]) + score_mat[i - 1][j - 1]
                if ali >= ivc and ali >= ihc:
                    path_mat[i][j] = '\\'
                    score_mat[i][j] = ali
                elif ihc >= ivc:
                    path_mat[i][j] = '|'
                    score_mat[i][j] = ihc
                else :
                    path_mat[i][j] = '-'
                    score_mat[i][j] = ivc

 # Gaps at the end of the sequences */
        j = shape[1] - 1;
        for i in range(1, shape[0]):
            ivc = score_mat[i - 1][j] + ge
            if path_mat[i - 1][j] == '\\':
                ivc += ge
            if ivc > score_mat[i][j]:
                path_mat[i][j] = '|'
                score_mat[i][j] = ivc

        i = shape[0] - 1
        for j in range(1, shape[1]):
            ihc = score_mat[i][j - 1] + ge
            if path_mat[i][j - 1] == '\\':
                ihc += go
            if ihc > score_mat[i][j]:
                path_mat[i][j] = '-'
                score_mat[i][j] = ihc


        self.score_mat = score_mat
        self.path_mat = path_mat
        self.shape = shape


        return Alignment(e1=entityOne, e2=entityTwo, score_mat=score_mat, path_mat=path_mat, matchCost=matchCost)


class Alignment(object):

    def __iter__(self):
        for i,e in enumerate(self.aliArrayOne):
            yield  self.aliArrayOne[i], self.aliArrayTwo[i]

    def viewer(self):
        return viewer(self)

    def __init__(self, score_mat=None, path_mat=None, e1=None, e2=None, matchCost=None, fileName=None, string=None):
        self.simPct = None
        self.idPct = None
        self.e1 = e1
        self.e2 = e2

        if fileName or string:
            self.parse(fileName=fileName, string=string)
        else :
            self.score_mat = np.copy(score_mat)
            self.path_mat = np.copy(path_mat)
            self.scorer = matchCost
            self.simPct = None


        if not self.simPct and not matchCost:
            raise ValueError("Cant compute similarity percentage")

        self.score = self.score_mat[self.score_mat.shape[0] - 1][self.score_mat.shape[1] - 1]
        self._backtrack()

    def _backtrack(self):
        i = self.score_mat.shape[0] - 1
        j = self.score_mat.shape[1] - 1


        self.aliArrayOne = []
        self.aliArrayTwo = []

        while i >= 0 and j >= 0 and self.path_mat[i][j] != '*':
            #print '_backtrack step : [' + str(i) + ', ' + str(j) + '] : ' + str(self.path_mat[i][j])
            if self.path_mat[i][j] == '\\':
                self.aliArrayOne.insert(0, self.e1[i - 1])
                self.aliArrayTwo.insert(0, self.e2[j - 1])
                i -= 1
                j -= 1
            elif self.path_mat[i][j] == '|':
                self.aliArrayTwo.insert(0, '-')
                self.aliArrayOne.insert(0, self.e1[i - 1])
                i -= 1
            elif self.path_mat[i][j] == '-':
                self.aliArrayOne.insert(0, '-')
                self.aliArrayTwo.insert(0, self.e2[j - 1])
                j -= 1
            else:
                raise ValueError("Error in backtracking at " + str(i) +","+ str(j) + "==>" + str(self.path_mat[i][j]))

        idPct = 0
        simPct = 0

        i = -1
        j = -1
        for n in range(0, len(self.aliArrayOne)):
            if str(self.aliArrayOne[n]) != '-':
                i += 1
            if str(self.aliArrayTwo[n]) != '-':
                j += 1
            if str(self.aliArrayOne[n]) == '-' or str(self.aliArrayTwo[n]) == '-':
                continue
            if self.aliArrayOne[n] == self.aliArrayTwo[n]:
                idPct += 1
            if not self.simPct:
                if self.scorer(self.aliArrayOne[n], self.aliArrayTwo[n]) > 0:
                    simPct += 1

        self.idPct = round(float(idPct) / len(self.aliArrayOne) * 100, 2)
        if not self.simPct:
            self.simPct = round(float(simPct) / len(self.aliArrayOne) * 100, 2)

    def _repr_html_(self):
        w = max(map(len,str(self).split()))
        return '<pre style="overflow-x : auto; width:' + str(int(w + 1)) + 'em">' + str(self) + '</pre>'

    def __repr__(self):
        string = "#Alignment score " + str(round(self.score, 2)) + ", identity(%) = " + str(self.idPct) + ", similarity(%) = " + str(self.simPct) + "\n"
        string += ">" + self.e1.id + "\n"
        if self.e1.hasSse and self.e2.hasSse:
            string += ''.join([ e.ss2 if e!= '-' else 'x' for e in self.aliArrayOne ]) + "\n"
        string += ''.join([ str(e) for e in self.aliArrayOne ]) + "\n"
        string += ''.join([ str(e) for e in self.aliArrayTwo ]) + "\n"
        if self.e1.hasSse and self.e2.hasSse:
            string += ''.join([ e.ss2 if e!= '-' else 'x' for e in self.aliArrayTwo ]) + "\n"
        string += ">" + self.e2.id + "\n"
        return string


        # Ajax purpose expected data structure
   #{
   #        name : 'some protein some protein some protein some protein some protein some protein some protein some protein some protein some protein some protein some protein some protein some protein some protein some protein A',
   #        aa  : 'FLGNPLG----NPLGNPLGNPLGNPLGNPLGNPLGNPLGNPLGN-----PLGNPLGNPFLGNPLG----NPLGNPLGNFLGNPLG----NPLGNPLGNFLGNPLG----NPLGNPLGNFLGNPLG----NPLGNPLGN',
   #        ss2 : 'hhhhhhh----cccccceeeeeeeeccccccchhhhhhhhhhhh-----cchhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh',
   #    },
    def ajax(self):
    # Offset for aa numbering is extract from the name string
    # safe as it comes form PfamCutter, hmmer output seq_range scalar


        m1 = re.search("\(([\d]+)", self.e1.id)
        m2 = re.search("\(([\d]+)", self.e2.id)

        return {'id' : self.idPct,
                'sim' : self.simPct,
                'ali' :
                [ {
                    'startsAt' : m1.group(1) if m1 else 1,
                    'name' : self.e1.id,
                    'aa'   : ''.join([ str(e) for e in self.aliArrayOne ]),
                    'ss2'  : ''.join([ e.ss2 if e!= '-' else 'x' for e in self.aliArrayOne ])
                },
                {
                    'startsAt' : m2.group(1) if m2 else 1,
                    'name' : self.e2.id,
                    'aa'   : ''.join([ str(e) for e in self.aliArrayTwo ]),
                    'ss2'  : ''.join([ e.ss2 if e!= '-' else 'x' for e in self.aliArrayTwo ])
                    }
                ]
            }

    def serialize(self, fileName=None):
        memfile1 = StringIO.StringIO()
        np.save(memfile1, self.score_mat)
        memfile1.seek(0)
        memfile2 = StringIO.StringIO()
        np.save(memfile2, self.path_mat)
        memfile2.seek(0)
        score_mat_json = json.dumps(memfile1.read().decode('latin-1'))
        path_mat_json = json.dumps(memfile2.read().decode('latin-1'))
        data = { 'e1' : self.e1.id, 'e2' : self.e2.id, 'score_mat' : score_mat_json, 'path_mat' : path_mat_json, 'simPct' : self.simPct }

        if fileName:
            with open(fileName, "w") as f:
                f.write(json.dumps(data))
            return
        return json.dumps(data)

    def parse(self, fileName=None, string=None):
        if fileName:
            with open(fileName, "r") as f:
                serialized = f.read()
            data = json.loads(serialized)
        else:
            data = json.loads(string)
        #print serialized
        if self.e1.id != data['e1'] or self.e2.id != data['e2']:
            raise ValueError("peptides missmatch:\n" + self.e1.id +"/"+self.e2.id + " vs " + data['e1'] + "/" + data['e2'] )

        memfile1 = StringIO.StringIO()
        memfile2 = StringIO.StringIO()
        memfile1.write(json.loads(data['score_mat']).encode('latin-1'))
        memfile2.write(json.loads(data['path_mat']).encode('latin-1'))
        memfile1.seek(0)
        memfile2.seek(0)
        self.score_mat = np.load(memfile1)
        self.path_mat = np.load(memfile2)

        self.simPct = data['simPct']


# latin-1 maps byte n to unicode code point n
#And to deserialize:

#memfile = StringIO.StringIO()
#memfile.write(json.loads(serialized).encode('latin-1'))
#memfile.seek(0)
#a = numpy.load(memfile)





