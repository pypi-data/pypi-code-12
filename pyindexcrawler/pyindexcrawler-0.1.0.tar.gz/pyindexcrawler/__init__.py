import urllib
import requests
import HTMLParser
from bs4 import BeautifulSoup
import xlsxwriter

myVar = 'this is a test'
root = 'https://nvusmeqlvdrepo.ra-int.com/repo/'

class PythonScrape(object):

    def __init__(self, url):
        self.index = url

    def get_document(self):
        doc = None
        try:
            doc = requests.get(self.index, verify=False).text
        except:
            print('There was an error trying to parse the URL')

        print 'Requests parsed : \n' + doc 
        return doc 

    def turnsoup(self, soup):
        temp = None
        try:
            txt = self.get_document(self)
            temp = BeautifulSoup(txt, "lxml")
        except Exception as ex:
            print ('There was an error using Beautiful Soup')
            print ("Error %s" % ex)
        
        thing = temp.findAll('a')
        for i in thing:
            print i
        return temp

    def xlsxwrite(self, col, row, xls):
        self.col = col
        self.row = row
        workbook = xlsxwriter.Workbook('test.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.set_column(col, row, 20)
        worksheet.write(row, col, xls)
        workbook.close()


if __name__ == "__main__":
    newScrape = PythonScrape(root)
    newScrape.get_document()
    newScrape.turnsoup(root)

    test = 'this is another test'
    newScrape.writetocsv(test)
    newScrape.xlsxwrite(0, 1, 'This is a test')


