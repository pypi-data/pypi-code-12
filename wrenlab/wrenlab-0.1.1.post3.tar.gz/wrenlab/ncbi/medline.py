"""
Parser for MEDLINE XML files.

Example:

.. code-block:: python
   
    from wrenlab.ncbi.medline import parse

    path = "http://www.nlm.nih.gov/databases/dtd/medsamp2013.xml.gz"
    with parse(path) as h:
        for article in path:
            print(article)
"""

import datetime
import locale
import re
import os
import multiprocessing as mp
import gzip
import pickle
import xml.etree.ElementTree as ET

from collections import namedtuple

__all__ = ["parse", "Article", "Journal"]

Article = namedtuple("Article", 
                     "id title abstract publication_date journal")
Journal = namedtuple("Journal", "id issn name")

class MedlineXMLFile(object):
    # FIXME: Date parsing will probably only work if system
    #   locale is US English

    _months = dict((i, locale.nl_langinfo(getattr(locale, "ABMON_" + str(i))))
                        for i in range(1,13))
    _non_digit_regex = re.compile(r"[^\d]+")

    def __init__(self, path):
        self._is_open = True
        self._handle = gzip.open(path, "rb")
    
    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def close(self):
        if self._is_open:
            self._handle.close()
            self._is_open = False
    
    def _text(self, xpath):
        try:
            return self._current_element.findall(xpath)[0].text
        except IndexError:
            return None

    def _strip_non_digit(self, text):
        return self._non_digit_regex.sub('', text)

    def _parse_citation(self):
        # Parse Article information
        pmid = int(self._text(".//PMID"))
        title = self._text(".//Article/ArticleTitle")
        abstract = self._text(".//Article/Abstract/AbstractText")

        publication_date = None
        year = self._text(".//Article/Journal/JournalIssue/PubDate/Year")
        if year:
            month = self._text(".//Article/Journal/JournalIssue/PubDate/Month")
            month = self._months.get(month, "01")
            day = self._text(".//Article/Journal/JournalIssue/PubDate/Day") or "01"
            publication_date = datetime.date(int(year), int(month), int(day))

        # Parse Journal information
        journal_id = self._text(".//MedlineJournalInfo/NlmUniqueID")
        journal_id = int(self._strip_non_digit(journal_id))
        journal_issn = self._text(".//MedlineJournalInfo/ISSNLinking")
        journal_name = self._text(".//MedlineJournalInfo/MedlineTA")
        journal = Journal(journal_id, journal_issn, journal_name)

        return Article(pmid, title, abstract, publication_date, journal)

    def __iter__(self):
        for event, element in ET.iterparse(self._handle):
            if event == "end" and element.tag == "MedlineCitation":
                self._current_element = element
                yield self._parse_citation()

def parse(path_or_handle, lazy=False):
    o = MedlineXMLFile(path_or_handle)
    if lazy:
        return o
    else:
        return list(o)

def parse_all(medline_dir):
    pool = mp.Pool(mp.cpu_count() - 2)
    paths = [os.path.join(medline_dir, p) 
            for p in os.listdir(medline_dir) if p.endswith(".xml.gz")]
    seen = set()
    for articles in pool.imap(parse, paths):
        for article in articles:
            if article.id in seen:
                continue
            seen.add(article.id)
            yield article

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("medline_xml_file", nargs="+")
    args = parser.parse_args()
    
    for path in args.medline_xml_file:
        with parse(path) as articles:
            for article in articles:
                if not article.title:
                    continue
                text = article.title
                if article.abstract:
                    text = " ".join([text, article.abstract])
                print(article.id, text, sep="\t")
