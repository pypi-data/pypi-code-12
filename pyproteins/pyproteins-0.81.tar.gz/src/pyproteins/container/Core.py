import urllib2
import json
from bs4 import BeautifulSoup

class Container():
    def __init__(self, id, url=None, fileName=None):
        if not id:
            raise ValueError("identifier is empty")
        self.id = id
        self.rawData = None
        self.url = url
        self.fileName = fileName

    def getXmlHandler(self):
        self.rawData = self._fetch() if not self.fileName else self._readFile()
        xmlH = BeautifulSoup(self.rawData, 'xml')
        return xmlH

    def _readFile(self):
        with open (self.fileName, "r") as f:
            rawData = f.read()
        return rawData

    def _fetch(self):
        print "DL " + self.url
        try:
            response = urllib2.urlopen(self.url)

        except urllib2.HTTPError as error:
            print self.url
            print "HTTP ERROR " + str(error.code)
            return None
        except urllib2.URLError as error:
            print self.url
            print error.reason
            return None
        rawData = response.read()
        response.close()
        return rawData

    def serialize (self):
        return self.rawData

    @property
    def raw(self):
        if not self.rawData:
            self.rawData = self._fetch() if not self.fileName else self._readFile()
        return self.rawData
