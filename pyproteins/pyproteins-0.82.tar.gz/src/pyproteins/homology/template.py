from Bio.PDB import *
import pyproteins.sequence.peptide
import copy
import pyproteins.sequence.msa
import os
import pyproteins.homology.core
import pyproteins.services.utils
from shutil import copyfile
import string

'''
    One or several pdb files
    A pepidic sequence or msa

    Do a msa on the pdb extracted sequences
    Do a msa on the peptidic sequence.
    Do a NW alignement between the two
'''


PDBparser = PDBParser()

def makeAll(templateList, bMsa=True, bPsipred=False, workDir=os.getcwd(), bSge=False, force=False, blastDbRoot=None, blastDb=None):

    if bSge:
        blastBean  = {
            'env' : 'sge',
            'blastDb' : blastDb,
            'blastDbRoot' : blastDbRoot,
            'rootDir' : workDir,
            'bPsipred' : bPsipred,
            'bBlast' : bMsa,
            'blastExecParam' : { '-j' : 8 }
        }

        if bMsa:
            tmpPeptideSet = pyproteins.sequence.peptide.EntrySet(name="templateMakeTmpSet")
            for tObj in templateList:
                tmpPeptideSet.add(tObj.peptide)
            res = tmpPeptideSet.blastAll(blastBean, blastXmlOnly=True)
            # This assumes all job went well
            # should make it more flexible
            for i, tObj in enumerate(templateList):
                tObj.bind(psiBlastOutputXml=res[i]['msa'])
                tObj.store(psiBlastOutputXml=res[i]['msa'], tag='_GPCRs', bMsa=True)


def fastaFileToList(file):
    comment = ''
    data = []
    with open(file, 'r') as input:
        for line in input:
            if line.startswith(">"):
                comment += line
            else:
                data += line.split()
    return { 'header' : comment, 'data' : data }

class TemplatePeptide(pyproteins.sequence.peptide.Entry):
    def __init__(self, datum):
        pyproteins.sequence.peptide.Entry.__init__(self, id=datum['id'])
        self.pdbnum = []

# pdbnum fasta/Seqres num conversion, fasta/Seqres numbering starts at 1
# translating pdbnum -> seqres returns a int
# translating seqres -> pdbnum returns a string

    def numTranslate(self, seqNum=None, pdbNum=None):
        if not seqNum and not pdbNum:
            raise ValueError, 'must provide a sequence or pdb number'

        if pdbNum:
            if not str(pdbNum) in self.pdbnum:
                raise ValueError, 'No such PDB number ' + str(pdbNum) + '\n' + str(self.pdbnum)
            else:
                i = self.pdbnum.index(str(pdbNum))
                return (i + 1)
                #print 'found pdb num ' + str(pdbNum) + 'at pos ' + str(i) + '\n'
                #return self.aaSeq[i]

# if fasta based position asked
        i = seqNum - 1
        if self.isPdbDefined(i):
            return self.pdbnum[i]
        return False

    def isPdbDefined(self, index):
        if (index < 1 ) or (index > len(self.pdbnum)):
            raise ValueError, '\'' + str(index) + '\' out of bonds\n'
        for c in str(self.pdbnum[index - 1]):
            if c not in string.printable:
                return False
        return True


class Template(pyproteins.homology.core.Core):

    def __repr__(self):
        #if self.structure:

        return str(self.peptide)

    def __init__(self, pdbSource, modelID=None, chain=None, folder=None, id=None):
        _id = id if id else os.path.basename(pdbSource)
        pyproteins.homology.core.Core.__init__(self, id=_id)
        self.structure = None
        self.pdbSeq = None
        self.pdbSourcePath = pdbSource
        self.folder = folder
        self.pdbSource = PDBparser.get_structure('mdl', pdbSource)
        model = self.pdbSource[0] if not modelID else self.pdbSource[modelID]
        #By default we use first chain atom coordinates record, user defined alternative chain w/
        # chain argument
        chainIdSorted = [ key for key, value in sorted(model.child_dict.items()) ]
        self.structure = model[chainIdSorted[0]] if not chain else model[chain]

        # Extract CA sequence and compute pairwise dist
        self.pdbSeq = [ r['CA'] for r in self.structure if 'CA' in r ]

        self.peptide = TemplatePeptide({ 'id' : self.id })

        self._setFromFolder()
        #if not self.peptide.seq:
        #    self.peptide.seq.pdbSeq
        print 'Template ' + self.id + ' loaded'

    def numTranslate(self, pdbNum=None, seqNum=None):
        val = self.peptide.numTranslate(pdbNum=pdbNum, seqNum=seqNum)
        return val
    def isPdbDefined(self, index):
        val = self.peptide.isPdbDefined(index)
        return val

    def store(self, tag='', psiBlastOutputXml=None, bMsa=False):
        fPath = self.folder if self.folder else os.getcwd()
        if psiBlastOutputXml:
            fPathX = pyproteins.services.utils.getAvailableTagFile(fPath + '/' + self.id + tag + '.blast')
            copyfile(psiBlastOutputXml, fPathX)
        if bMsa:
            fPathM = pyproteins.services.utils.getAvailableTagFile(fPath + '/' + self.id + tag + '.mali')
            self.mAli.fastaDump(outputFile=fPathM)


    ## initialize object attributes from a make core folder if any provided
    def _setFromFolder(self):
        if not self.folder:
            return False
        # pdbnum
        for file in os.listdir(self.folder):
            #print file
            fPath = self.folder + '/' + file
            if file.endswith('.pdbnum'):
                data = fastaFileToList(fPath)
                self.peptide.pdbnum = data['data']
            if file.endswith('.fasta'):
                data = fastaFileToList(fPath)
                self.peptide.seq = ''.join(data['data'])
                self.peptide.desc = data['header']
            if file.endswith('.psipred_ss2'):
                self.peptide.ss2Bind(file=fPath)
            if file.endswith('.blast'):
                self.bind(psiBlastOutputXml=fPath)

        self.bind(psipredFolder=self.folder)


    @property
    def aaSeq(self):
        if self.fasta:
            return self.fasta
        #for atom in self.sequence
        return [ (Peptide.threeToOne(atom.get_parent().resname)) for atom in self.pdbSeq ]





