from core import RealPred
from memory_profiler import profile

class X():
    __slots__ = ['lemma','pos','sense']
    def __eq__(self, other):
        if self.lemma == other.lemma and self.pos == other.pos and self.sense == other.sense:
            return True
        else:
            return False
    def __init__(self,lemma,pos,sense):
        self.lemma = lemma
        self.pos = pos
        self.sense = sense

@profile
def bla():
    return [X('cat','n','1') for _ in range(1000000)]

bla()