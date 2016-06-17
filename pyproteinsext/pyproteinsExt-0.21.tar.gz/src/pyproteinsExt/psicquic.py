from bioservices import WSDLService
import urllib2
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET


PSQ_FIELDS= ["idA", "idB", "altA", "altB", "aliasA", "aliasB", "interactionDetectionMethod", "firstAuthor", "pubid", "taxidA", "taxidB",
            "interactionTypes", "sourceDatabases", "interactionIdentifiers", "confidenceScore", "complexExpansion", "biologicalRoleA"
            , "biologicalRoleB", "experimentalRoleA", "experimentalRoleB", "interactorTypeA", "interactorTypeB", "xRefA", "xRefB",
            "xRefInteraction", "annotationA", "annotationB", "annotationInteraction", "taxidHost", "parameters", "creationDate",
            "updateDate", "checksumA", "checksumB", "negative", "featuresA", "featuresB", "stoichiometryA", "stoichiometryB",
            "identificationMethodA", "identificationMethodB"]


class OLS():

    def __init__(self, ontology=None):
        self.cOntology = "MI"
        self.api = WSDLService("OLS", "http://www.ebi.ac.uk/ontology-lookup/OntologyQuery.wsdl")
        if ontology: self.cOntology = ontology
        self.lineage = {}

    def isSonOf(self, childId=None, parentId=None):
        if not childId or not parentId:
            return None
        self._getLineage(parentId)
        if childId in self.lineage[parentId]: return True
        return False

    def _getLineage(self, termId):
        if termId in self.lineage:
            return
        ans = self.api.serv.getTermChildren(termId, self.cOntology, 1000)
        if hasattr(ans, 'item'):
            self.lineage[termId] = [ i.key for i in ans.item ]
        else:
            self.lineage[termId] = []

    def getTermById(self, termId=None):
        ans = self.api.serv.getTermById(termId, self.cOntology)
        print ans
        if ans == termId:
            print "id term failed"
            return None

class PSICQUIC():
    mitabLvls = ["25", "27"]
    olsWebService = OLS()

    def __len__(self):
        return len (self.records)

    def __init__(self, registryUrl="http://www.ebi.ac.uk/Tools/webservices/psicquic/registry/registry?action=STATUS&format=xml", mode='STRICT'):
        self.registry = self.getRegistry(registryUrl)
        self.records = []
        self.mode = mode # or 'LOOSE'
        self.registredPublications = {} # { "pubid" : "sourceDatabase" }
        if not self.registry:
            self.registry = registry()

    def __repr__(self):
        string = "\n".join(map(str, self.records))
        return string

    def __iter__(self):
        for record in self.records:
            yield record

    def clear(self):
        self.records = []
        self.registredPublications = {}

    def dump(self, file=None):
        if file:
            with open(file, 'w') as f:
                f.write(self.__repr__())
        else:
            print self.__repr__()

    def load(self, mitabFile=None):
        if not mitabFile:
            print "You must provide a mitabFile"
            return
        bufferStr = ""
        with open (mitabFile) as inp:
            for line in inp:
                bufferStr = bufferStr + line
        self._parse(bufferStr)

    def query(self, providers=["dip"], uniprotId=None, mitabLvl="25"):
        if mitabLvl not in self.mitabLvls:
            print "invalid mitab level " + mitabLvl
            return None
        if not uniprotId:
            print "uniprotId parameter must be provided"
            return

        for provider in providers:
# psicquic members
            if not provider in self.registry:
                print "provider is no registred database"
                continue

            miql = self.registry[provider] + "query/id:" + uniprotId + "?format=tab" + mitabLvl
            print miql
            ans = self._ping(miql)
            if ans == 0:
                miql = self.registry[provider] + "query/id:" + uniprotId + "?format=tab25"
                ans = self._ping(miql)
            if ans:
                self._parse(ans)
            else:
                continue

    def _ping(self, url):
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as error:
            if error.code == 406:
                print url
                print "mitab Level may not be supported retrying w/ 2.5"
                return 0
            print url + "\nHTTP ERROR " + str(error.code)
            return None
        except urllib2.URLError as error:
            print url + "\n" + str(error.reason)
            return None
        raw = response.read()
        response.close()
        return raw

    def getRegistry(self, url):
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError as error:
            print "Unable to contact registry at " + url
            print "Loading default"
            return registry()

        raw = response.read()
        response.close()
        return registry(raw)



    def _parse(self, raw):
        bufferRecords = [PSQDATA(line) for line in raw.split("\n") if len(line) > 0]
        if self.mode is "LOOSE":
            self.records = self.records + bufferRecords
        else:
            self.records = self.records + [data for data in bufferRecords if self._checkPsqData(data)]

    def _checkPsqData (self, psqDataObj):
        pmid = psqDataObj['pmid']
        source = psqDataObj['source']
        if not pmid in self.registredPublications:
            self.registredPublications[pmid] = source
            return True

        if self.registredPublications[pmid] == source:
            return True
        else:
            print "Warning publication " + pmid + " provided by " + source + " has already been fetched from " + self.registredPublications[pmid]
            return False

    def analyse(self):
        if len(self) == 0: return None
        data = {
            "stats" : self.statInteractionMethods(),
            "pmids" : self.countPmid()
        }
        return data

    def countPmid(self):
        knownPmids = []
        for record in self.records:
            if record['pmid'] not in knownPmids:
                knownPmids.append(record['pmid'])
        return knownPmids

    def statInteractionMethods(self):
        stats = {
            "MI:0401" : { "name" : "biochemical", "count" : 0},
            "MI:0013" : { "name" : "biophysical", "count" : 0},
            "MI:0254" : {"name":"genetic interference","count" : 0},
            "MI:0428" : { "name" : "imaging technique", "count" : 0},
            "MI:1088" : { "name" : "phenotype-based detection assay", "count" : 0},
            "MI:0255" : { "name" : "post transcriptional interference", "count" : 0},
            "MI:0090" : {"name":"protein complementation assay","count":0},
            "MI:0362" : { "name" : "inference", "count" : 0},
            "MI:0063" : {"name":"interaction prediction","count":0},
            "MI:0686" : { "name" : "unspecified method", "count" : 0}
        }
        stillExperimental = 0
        for psqDataObj in self:
            detectMeth = psqDataObj["interactionDetectionMethod"]
            boolT = False
            if detectMeth in stats:
                stats[detectMeth]['count'] = stats[detectMeth]['count'] + 1
                continue
            for id in stats:
                if self.olsWebService.isSonOf(detectMeth, id):
                    stats[id]['count'] = stats[id]['count'] + 1
                    boolT = True
                    break
            if not boolT:
                if detectMeth == "MI:0045":
                    stillExperimental = stillExperimental + 1
                else:
                    print "Warning " + detectMeth + " was not cast"

        stats["experimental"] = stillExperimental
        #print stats
        #print "\tstill Experimental => " + str(stillExperimental)
        return stats

# This is the main interface we try to define smart __getitem__() access keys
class PSQDATA():
    def __init__(self, raw):
        self.raw = raw
        self.data = [PSQDATUM(column) for column in raw.split("\t")]
    def __repr__(self):
        string = "\t".join(map(str,self.data))
        return string
    def __getitem__(self, key):
        if key is "pmid":
            for field in self.data[8].data:
                if field.type == "pubmed:":
                    return field.value
            return self.data[8].data[0].value
        if key is "source":
            if self.data[12].data[0].annotation:
                return self.data[12].data[0].annotation
            return self.data[12].data[0].value
        if key is "interactionDetectionMethod":
            return self.data[6].data[0].value

    def getNames(self):
        pass

class PSQDATUM():
    def __init__(self, string):
        self.raw = string
        self.data = [ PSQFIELD(field) for field in string.split('|')]
    def __repr__(self):
        string = '|'.join(map(str,self.data))
        return string

class PSQFIELD():
    fieldParser = re.compile('^([^:^"]+:){0,1}"{0,1}([^"\(]+)"{0,1}\({0,1}([^\)]+){0,1}\){0,1}$')
    def __init__(self, raw):
        m = re.match(self.fieldParser, raw)
        if not m:
            print "warning following field causes problem to parse\n" + raw
            self.value = raw
            self.type = None
            self.annotation = None
        else:
            self.type = m.groups()[0]
            self.value = m.groups()[1]
            self.annotation = m.groups()[2]
    def __repr__(self):
        string = self.value
        if self.type: string = self.type + string
        if self.annotation: string = string + "(" + self.annotation + ")"
        return string



class registry():
    data = {
        'dip' : "http://imex.mbi.ucla.edu/psicquic-ws/webservices/current/search/",
        'intact' : "http://www.ebi.ac.uk/Tools/webservices/psicquic/intact/webservices/current/search/",
        'mint' : "http://www.ebi.ac.uk/Tools/webservices/psicquic/mint/webservices/current/search/",
        'innatedb_imex' : "http://www.ebi.ac.uk/Tools/webservices/psicquic/innatedb/webservices/current/search/",
        'matrixdb' : "http://matrixdb.ibcp.fr:8080/psicquic/webservices/current/search/",
        'innatedb' : "http://psicquic.curated.innatedb.com/webservices/current/search/"
    }

    def __init__(self, raw):
        if raw:
            #print raw
            root = ET.fromstring(raw)
            for child in root:
                name = ""
                url = ""
                for subT in child:
                    if subT.tag == "{http://hupo.psi.org/psicquic/registry}restUrl":
                        url = subT.text
                    if subT.tag == "{http://hupo.psi.org/psicquic/registry}name":
                        name = subT.text
                name = name.lower().replace("-","_")
                self.data[name] = url

                '''
                if not line:
                    continue
                #print line
                field = line.split("=")
                name = field[0].lower().replace("-","_")
                self.data[name] = field[1]
                '''

    def __getitem__(self,index):
        if not index in self.data:
            return None
        return self.data[index]

    def __repr__(self):
        string = ""
        for db in self.data:
            string = string + db + " : " + self.data[db] + "\n"
        return string

    def __iter__(self):
        for db in self.data:
            yield db
