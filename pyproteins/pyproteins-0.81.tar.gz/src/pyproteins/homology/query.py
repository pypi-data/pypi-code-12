from Bio.PDB import *
import pyproteins.sequence.peptide
import pyproteins.services.utils
import copy
import pyproteins.sequence.msa
import pyproteins.sequence.psipred
import pyproteins.homology.core
import os.path


#pyproteins.services.utils.checkEnv("HHLIB")

class Query(pyproteins.homology.core.Core): # Possible input, aa sequence string or mfasta file or mfasta bean
    def __init__(self, **kwargs):
        pyproteins.homology.core.Core.__init__(self, **kwargs)

    def __repr__(self):
        string = "Query ID : " + self.id + '\n'
        string += super(Query, self).__repr__()
        return string

    def make(self, bSge=False, workDir=None, force=False, blastDbRoot=None, blastDb=None, psipredScript=None, psipredDbRoot=None):
        # check ss2/ msa status
        bSse = False if self.sse else True
        bMsa = False if self.mAli else True

        if workDir:
            pyproteins.services.utils.mkdir(workDir)
        else :
            workDir = os.getcwd()

        if bSge:
            blastBean  = {
                'env' : 'sge',
                'blastDb' : blastDb,
                'blastDbRoot' : blastDbRoot,
                'rootDir' : workDir,
                'bPsipred' : bSse,
                'bBlast' : bMsa,
                'ps' : bMsa,
                "psipredDbRoot" : psipredDbRoot,
                'psipredScript' : psipredScript
            }
            tmpPeptideSet = pyproteins.sequence.peptide.EntrySet(name="queryMakeTmpSet")
            tmpPeptideSet.add(self.peptide)
            res = tmpPeptideSet.blastAll(blastBean)
            if bMsa:
                self.bind(msaObj=res[0]['msa'])
            if bSse:
                self.bind(psipredContainer=res[0]['sse'])

        else :
            print "Enriching query data WITHOUT cluster ressources (did not found --sge flag)"
            # dump batch

def loadFromBean(beanFile):

    coreObject = pyproteins.homology.core.loadFromBean(beanFile)
    # does not work
    #coreObject.__class__ = Query
    #return coreObject
    queryObject = Query(id=coreObject.id)
    queryObject.bind(peptide=coreObject.peptide, psipredContainer=coreObject.sse, msaObj = coreObject.mAli)
    return queryObject
