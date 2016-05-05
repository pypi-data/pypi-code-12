import MySQLdb
import os, urllib, time
from PubmedArticleSet import *
from xml.etree import ElementTree
import xml.etree.cElementTree as ET
import glob

## Check to make sure all the pmids given can be found in the XML file given.
# @param ids The ids of the documents to look for.
# @param filename The PubmedArticleSet XML file to look at
# return True if all ids found (and exactly those ids), False otherwisec
"""
This class is for downloading all pubmed articles that associated to gene ontology terms 

example of using this class:
pubmed_directory is the directory that user wants to store the pubmed articles 
parsedPubMed_directory is the directory that user wants to store parsed pubmed
tool = downloadPubMed(host, user, password, dbname, pubmed_directory, parsedPubMed_directory)
tool.parse()
"""

class DownloadPubMed: 
    def __init__(self, host, user, password, dbname, pubmed_directory, parsedPubMed_directory):
        self.db = MySQLdb.connect(host, user, password, dbname)
        self.ids = self.getPMIDs()
        self.directory = pubmed_directory
        self.parsedPubMeds = parsedPubMed_directory

    def getPMIDs(self):
        PMIDs=[]
        cursor = self.db.cursor()
        query = "select distinct(pmid) from final_term_evidence"
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            PMIDs.append(row[0])
        return PMIDs;

    def verifyDocuments(self, ids, filename):
        handler = PubmedArticleSet.parse(filename)
        pmids = handler.docs.keys()
        
        notfound = set()
        extrafound = set()
        for pmid in pmids:
            if not pmid in ids:
                extrafound.add(pmid)
        for gid in ids:
            if not gid in pmids:
                notfound.add(gid)

        result = True
        if len(extrafound) > 0:
            #raise RuntimeWarning, "There were %i extra pmids downloaded: %s" % (len(extrafound), ",".join(extrafound))
            print "There were %i extra pmids downloaded: %s" % (len(extrafound), ",".join(extrafound))
            result = False
        if len(notfound) > 0:
            #raise RuntimeWarning, "There were %i pmids not downloaded: %s" % (len(notfound), ",".join(notfound))                
            print "There were %i pmids not downloaded: %s" % (len(notfound), ",".join(notfound))                
            result = False
        return result

    ## Fetch the pubmed documents given by their ids and store them in
    # xml format in the given directory
    # @param ids The ids to fetch
    # @param directory The directory to store the files in
    # @param blocksize The number to download at one time, default of 500
    # @param failIfProblem End program with error if there is a problem downloading
    # pubmed documents.  If False (default) only a warning message will be displayed.
    def efetchByBlock(self, blocksize=None, failIfProblem=False):
        blocksize = blocksize or 500
        url = "http://www.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        # ids = map(lambda x: str(int(x)), ids)
        size = int(float(len(self.ids)) / float(blocksize))
        # try:
        index = 0

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        while index < len(self.ids):
                end = min(index+blocksize, len(self.ids))           
                # if not os.path.exists(filename): 
                filename = os.path.join(self.directory, "block_%i.xml" % (index / blocksize))            
                outfile = open(filename, 'w')
                idblock = ",".join(self.ids[index:end])
                mysock = urllib.urlopen("%s?db=pubmed&id=%s&retmode=xml" % (url, idblock))
                line = mysock.readline()
                while line:
                    outfile.write(line)
                    line = mysock.readline()
                mysock.close()
                outfile.close()
                time.sleep(3)

                if not self.verifyDocuments(self.ids[index:end], filename) and failIfProblem:
                    print "PMID check verification failed - some documents not downloaded"
                    #raise RuntimeError, "PMID check verification failed - some documents not downloaded"
                index += blocksize
        # except Exception, e:
        #     raise RuntimeError, "Problem fetching all PMIDs."

    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def parse(self):
        self.efetchByBlock();
        files = glob.glob(os.path.join(self.directory, "*.xml"))
        for i in range(len(files)):
            filename = files[i]
            with open(filename, 'rt') as f:
                oldtree = ElementTree.parse(f)
            root=ET.Element("PubmedArticleSet");

            for article in oldtree.iter("MedlineCitation"):
                doc=ET.SubElement(root,"PubMedArticle");
                pmid=article.find("PMID").text
                title=article.find("Article").find("ArticleTitle").text
                ET.SubElement(doc, "PMID").text = pmid
                ET.SubElement(doc, "Title").text = title
                if article.find("Article").find("Abstract") is not None:
                    abstract=article.find("Article").find("Abstract").find("AbstractText").text 
                    ET.SubElement(doc, "Abstract").text = abstract
                elif article.find("Article").find("Abstract") is None:
                    pass
            newtree = ET.ElementTree(root)
            self.indent(root)
            if not os.path.exists(self.parsedPubMeds):
                os.makedirs(self.parsedPubMeds)
            newtree.write(os.path.join(self.parsedPubMeds, "files_%s.xml"%i))
