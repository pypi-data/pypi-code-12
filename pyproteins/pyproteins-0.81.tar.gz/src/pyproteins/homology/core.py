import pyproteins.services.utils
import json
import pyproteins.sequence.msa
import pyproteins.sequence.peptide

# A class to factorize method/attributes shared by query and template classes


#
# Constructor args
#   sequence{Bio.Seq}
#   fastaFile{filePath}
#   msaFile{mFasta filePath}
#

class Core(object):
    def __init__(self, **kwargs):
        self.mAli = None
        self.peptide = None
        self.sse = None
        self.id = None
        self.beanDatum = {
                            "comments" : None,
                            "id" : None,
                            "files" : {
                                "fasta" : None,
                                "blast" : None
                            },
                            "folders" : {
                                "psipred" : None
                                }
                        }

        if kwargs is not None:
            if 'id' in kwargs:
                self.id = kwargs['id']
            if 'sequence' in kwargs:
                print "loading peptide sequence " + kwargs['sequence']
                self.peptide = pyproteins.sequence.peptide.Entry(seq=kwargs['sequence'])
            elif 'fastaFile' in kwargs:
                self.peptide = pyproteins.sequence.peptide.Entry()
                self.peptide.parse(kwargs['fastaFile'])
                self.beanDatum['files']['fasta'] = kwargs['fastaFile']
            if 'msaFile' in kwargs:
                print "loading msa from file"
                msaObj = pyproteins.sequence.msa.Msa(fileName=kwargs['msaFile'])
                self.bind(msaObj=msaObj)

            if not self.id:
                if self.peptide:
                    self.id = self.peptide.id

            if not self.id:
                raise ValueError, 'No id provided'

    def __repr__(self):
        string = ''
        string += str(self.peptide) + '\n'
        if self.mAli:
            string += "Alignment number of sequences" + str(self.mAli.shape()[0]) + ', columns ' + str(self.mAli.shape()[1]) + '\n'
            #string += str(self.mAli) + '\n'
        if self.sse:
            string += str(self.sse) + '\n'
        return string

    @property
    def fasta(self):
        if self.peptide.seq:
            return self.peptide.seq
        return None

    # commenting it,  It will break a template call, TO FIX downstream
    #def msa(self, psiBlastOutputXml=None):
    #    if not self.mAli:
    #        if not psiBlastOutputXml:
    #            raise ValueError, 'No blast output available to generate ' + self.id + ' msa'
    #        self.mAli = peptide.blast(psiBlastOutputXml)
    #    return self.mAli

    def beanDump(self, filePath):
        self.beanDatum['id'] = self.id
        self.beanDatum['comments'] = "auto-generated query bean file"

        if filePath:
            with open(filePath, 'w') as fp:
                json.dump(self.beanDatum, fp)


    def bind(self, peptide=None, psipredFolder=None, msaObj=None, psipredContainer=None, psiBlastOutputXml=None):
        if psipredFolder:
            self.sse = pyproteins.sequence.psipred.parse(folder=psipredFolder)
            self.beanDatum['folders']['psipred'] = psipredFolder
        if msaObj:
            self.mAli = msaObj
        if psipredContainer:
            self.sse = psipredContainer
        if peptide:
            self.peptide = peptide
        if psiBlastOutputXml:
            self.mAli = self.peptide.blast(psiBlastOutputXml)
            self.beanDatum['files']['blast'] = psiBlastOutputXml


    def hhDump(self, filePath=None):
        string = '>ss_pred PSIPRED predicted secondary structure\n'
        string += pyproteins.services.utils.lFormat(self.sse.pred) + '\n'
        string += '>ss_conf PSIPRED confidence values\n'
        string += pyproteins.services.utils.lFormat(self.sse.conf) + '\n'
        string += self.mAli.fastaDump()
        if filePath:
            with open(filePath, 'w') as f:
                f.write(string)
        else:
            return string

def loadFromBean(beanFile):
    with open(beanFile) as json_file:
        bean = json.load(json_file)

    _checkBean(bean)

    coreObject = Core(id=bean['id'], fastaFile=bean['files']['fasta'])
    coreObject.bind(psipredFolder=bean['folders']['psipred'])
    coreObject.bind(psiBlastOutputXml=bean['files']['blast'])
    return coreObject

def _checkBean(bean):
    if not 'id' in bean:
        raise ValueError, 'No id found in bean \'' + beanFile + '\''
    if not 'files' in bean:
        raise ValueError, 'No files found in bean \'' + beanFile + '\''
    if not 'fasta' in bean['files']:
        raise ValueError, '\'files.fasta\' key missing in bean \'' + beanFile + '\''
    if not 'blast' in bean['files']:
        raise ValueError, '\'files.blast\' key missing in bean \'' + beanFile + '\''
    if not 'folders' in bean:
        raise ValueError, 'No folders found in bean \'' + beanFile + '\''
    if not 'psipred' in bean['folders']:
        raise ValueError, '\'folders.psipred\' key missing in bean \'' + beanFile + '\''

