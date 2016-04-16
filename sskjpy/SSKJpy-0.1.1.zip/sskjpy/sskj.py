__author__ = "DefaltSimon"
__name__ = "SSKJpy"
__version__ = "0.1.1"
__license__ = "MIT"

from bs4 import BeautifulSoup
import requests

class NotFound(Exception):
    pass

class SskjParser:
    def __init__(self,keyword):
        """Initializes the class, searching on bos.zrc-sazu.si immediately by keyword you passed
        All results are sorted by relevancy.

        Arguments:
        | keyword(str) - term you want to search
        """
        self.keyword = str(keyword)
        self.urltoget = "http://bos.zrc-sazu.si/cgi/a03.exe?name=sskj_testa&expression={}"
        self.htmlunparsed = requests.get(self.urltoget.format(self.keyword))
        self.bshtml = BeautifulSoup(self.htmlunparsed.content, "html.parser")

    def result(self):
        """Returns a definition of a word (with attributes and the keyword itself)
        Example: tést  -a m (ẹ̑) 1. postopek za ugotavljanje določenih lastnosti, sposobnosti...
        """
        fullsum = self.bshtml.find("ol",{"start":"1"}).find("li",attrs={"class":"nounderline"}).text
        for line in str(fullsum).splitlines():
            if True:
                fullsum = line
                break
        if str(fullsum).startswith("     "):
            fullsum = str(fullsum)[5:]
        if str(fullsum).endswith(",") or str(fullsum).endswith(":"):
            fullsum = str(fullsum)[:-1]
        return str(fullsum)

    def resultattributes(self):
        """Returns attributes of a word.
        Example: -a m (ẹ̑)
        """
        fullsum = self.bshtml.find("ol",{"start":"1"}).find("li",attrs={"class":"nounderline"}).text
        for line in str(fullsum).splitlines():
            if True:
                another = line
                break
        if str(another).startswith("     "):
            another = str(fullsum)[5:]
        keyword2 = self.bshtml.find("li",attrs={"class":"nounderline"}).find("b").text
        final = another[(len(str(keyword2))+2):]
        begins = final.index("1.")
        return final[:begins-1]
    def moredefinitions(self,number):
        """Returns <number>-th definition found in dictionary (sorted by relevancy)

        Arguments:
        | number(int) - the consecutive number of a definition that you want

        Example:
        term = "test"; number = 2
        The result would be "testament", because this word is closest to 'test' (after the 'test' itself).
        """
        if isinstance(number,int):
            pass
        elif isinstance(number,float):
            if number % 1 != 0:
                raise TypeError("var number must be an integer")
            number = int(number)
        else:
            raise TypeError("var number must be an integer")
        url = "http://bos.zrc-sazu.si/cgi/a03.exe?name=sskj_testa&expression={}&hs={}".format(self.keyword,int(number))
        self.htmlunparsed2 = requests.get(url.format(self.keyword))
        self.bshtml2 = BeautifulSoup(self.htmlunparsed2.content, "html.parser")

        fullsum = self.bshtml2.find("ol",{"start":int(number)}).find("li",attrs={"class":"nounderline"}).text
        count = 1
        for line in str(fullsum).splitlines():
            if count == 1:
                fullsum = line
                break
        if str(fullsum).startswith("     "):
            fullsum = str(fullsum)[5:]
        if str(fullsum).endswith(",") or str(fullsum).endswith(":"):
            fullsum = str(fullsum)[:-1]
        return str(fullsum)

    def shortsum(self):
        """Returns a short summary of a word.

        Example:
        keyword = "test"
        Would return "postopek za ugotavljanje določenih lastnosti, sposobnosti, znanja koga, preizkus"
        """
        shsum = self.bshtml.find("li",attrs={"class":"nounderline"}).find("i").text
        if str(shsum).endswith(":"):
            shsum = shsum[:-1]
        return str(shsum)

    def keyword(self):
        """Returns the first keyword.
        Sometimes the exact word can't be found in the dictionary, returning the closest word.
        In that case your initial keyword won't be correct. Use this to see the real keyword.
        """
        keyword = self.bshtml.find("li",attrs={"class":"nounderline"}).find("b").text
        return str(keyword)

    def terminology(self):
        """Returns the terminology part of a definition"""
        ht2 = str(self.bshtml.find("ol",{"start":"1"}).find("li",attrs={"class":"nounderline"}).text)
        try:
            beginning = ht2.index("◊")
        except ValueError:
            raise NotFound("No terminology defined for this keyword")
        try:
            end = ht2.index("♪")
            final = ht2[beginning+2:end-1]
        except ValueError:
            raise NotFound("Error occured, ♪ could not be found at the end. Weird?")

        return str(final)

    def slang(self):
        """Returns the slang part of a definition"""
        ht2 = str(self.bshtml.find("ol",{"start":"1"}).find("li",attrs={"class":"nounderline"}).text)
        try:
            beginning = ht2.index("●")
        except ValueError:
            raise NotFound("No slang examples defined for this keyword")
        try:
            end = ht2.index("◊")
            final = ht2[beginning+2:end-1]
        except ValueError:
            raise NotFound("Error occured, ◊ could not be found at the end. Weird?")

        return str(final)


# Ignore

#sskj = SskjParser("test")
#print(sskj.slang())
#print(sskj.resultattributes())
#print(sskj.terminology())
#print(sskj.result())
#print(sskj.moredefinitions(4))
#print(sskj.firstkeyword())
#print(sskj.shortsum())