# -*- coding: utf-8 -*-
"""
This module contains the object class for BibTeX parsing.

-------------------------------------------------------------------------------
"""

__license__ = "MIT"
__docformat__ = 'reStructuredText'
__revision__ = filter(str.isdigit, "$Revision: 215 $")


# import external modules
import re
from pybtex.database import parse_string

from ._latexenc import string_to_latex
from ._latexenc import latex_to_string
import sys
import codecs

if sys.version_info < (3,):
    pass
else:
    unicode = str


def _clear_comments(data):
    """
    Strips the comments and returns plain (BibTeX) data.

    :param data: input data
    :type data: st
    :return: plain data
    :rtype: str
    """
    res = re.sub(u'(%.*\n)', '', data)
    res = re.sub(u"(comment [^\n]*\n)", '', res)
    return res


def parse_data(data, decode=False):
    """
    (Wrapper) Function for parsing a (unicode) string of BibTeX data containing one or more entries
    and returns a list of dictionaries (records).

    .. note:: Uses :func:`pybtex.database.parse_string` for parsing.

    :param data: input BibTeX data
    :type data: unicode
    :return: list of dicts
    :rtype: list
    :raise pybtex.scanner.TokenRequired: If a citation-key is missed.
    :raises pybtex.database.BibliographyDataError: If a citation-key is used twice.
    """

    # private function
    def _person_list_to_string(personList):
        """
        Convert a list of pybtex's person objects to the BibTeX (unicode) string.

        :param personList: list of pybtex's person objects
        :return: BibTeX (unicode) string
        """
        for i in range(0, len(personList)):
            personList[i] = unicode(personList[i])
        return ' and '.join(personList)

    if decode:
        data = latex_to_string(data)

    # use pybtex's parser and get a BibliographyData object
    bib_data = parse_string(data, 'bibtex')

    # convert pybtex's BibliographyData object to a list of records
    records = []
    for key, entry in bib_data.entries.items():
        record = {}
        record['ENTRYTYPE'] = entry.type.encode('us-ascii', 'replace').decode('us-ascii')
        record['ID'] = entry.key.encode('us-ascii', 'replace').decode('us-ascii')

        # data fields
        for key, value in entry.fields.items():
            record[key.lower().encode('us-ascii', 'replace').decode('us-ascii')] = value

        # persons
        for pp in ['Author', 'Editor']:
            if entry.persons.get(pp):
                ppStr = _person_list_to_string(entry.persons[pp])
                record[pp.lower()] = ppStr

        records.append(record)

    return records


def parse_data_old(data):
    """
    Function parsing a string of BibTeX data containing one or more entries
    and returns a list of dictionaries.

    .. warning:: If a citation-key is used twice, the last Entry will win!

    :param data: input BibTeX data
    :type data: str
    :return: list of dicts
    :rtype: list
    """
    bibStr = _clear_comments(data)
    if decode:
        bibStr = latex_to_string(bibStr)
    bib = Parser(bibStr)
    bib.parse()
    return bib.records.values()


def record_to_bibtex(record, citeKey=None, encoding='ascii'):
    """
    Returns the BibTeX Entry string.

    :param record: record dictionary containing tags and their contents
    :type record: dict
    :param citeKey: citation-key
    :type: citeKey: str
    :return: BibTeX Entry string
    :rtype: str
    """

    if codecs.lookup(encoding) == codecs.lookup('ascii'):
        record = latex_encode_record(record)

    citeKey = citeKey or record.get('ID') or 'undefined'

    bibtex = ''

    # write BibTeX Entry type and citation-key
    bibtex += '@' + record['ENTRYTYPE'].capitalize() + '{' + citeKey

    # write BibTeX tags
    for tag in sorted(record):
        if tag not in ['ENTRYTYPE', 'ID']:
            bibtex += ",\n" + '	' + tag.capitalize() + " = {" + record[tag] + "}"
    bibtex += "\n}\n\n"
    return bibtex


def latex_encode_record(record):
    """
    Convert unicode character to LaTeX code.

    :param dict: BibTeX Entry dictionary
    :type dict: Entry.datadict
    :return: BibTeX Entry dictionary
    :rtype: Entry.datadict
    """
    protectedTags = ['doi', 'url', 'ENTRYTYPE', 'ID']
    for key, value in record.items():
        if key not in protectedTags:
            record[key] = string_to_latex(value)

    return record


class Parser():
    """Main class for BibTeX parsing

    This class is a modified version of Bibpy (yet another) BibTex file parser in python,
    published 2011 by Panagiotis Tigkas under the MIT licence.
    (https://github.com/ptigas/bibpy)

    :param data: plain BibTeX data
    :type data: str
    :return: BibTeX parser object
    :rtype: .parser.parser
    """

    def tokenize(self):
        for item in self.token_re.finditer(self.data):
            i = item.group(0)
            if self.white.match(i):
                if self.nl.match(i):
                    self.line += 1
                continue
            else:
                yield i

    def __init__(self, data):
        self.data = data
        self.token = None
        self.token_type = None
        self._next_token = self.tokenize().next
        self.hashtable = {}
        self.mode = None
        self.records = {}
        self.line = 1

        # compile some regexes
        self.white = re.compile(r"[\n|\s]+")
        self.nl = re.compile(r"[\n]")
        self.token_re = re.compile(r"([^\s\"#%'(){}@,=]+|\n|@|\"|{|}|=|,)")

    def parse(self):
        """Parses :py:attr:`data` and stores the parsed BibTeX entries to :attr:`.records`"""
        while True:
            try:
                self.next_token()
                while self.database():
                    pass
            except StopIteration:
                break

    def next_token(self):
        self.token = self._next_token()
        #print self.line, self.token

    def database(self):
        if self.token == '@':
            self.next_token()
            self.entry()

    def entry(self):
        if self.token.lower() == 'string':
            self.mode = 'string'
            self.string()
            self.mode = None
        else:
            self.mode = 'record'
            self.record()
            self.mode = None

    def string(self):
        if self.token.lower() == "string":
            self.next_token()
            if self.token == "{":
                self.next_token()
                self.field()
                if self.token == "}":
                    pass
                else:
                    raise NameError("} missing")

    def field(self):
        name = self.name()
        if self.token == '=':
            self.next_token()
            value = self.value()
            if self.mode == 'string':
                self.hashtable[name] = value
            return (name, value)

    def value(self):
        value = ""
        val = []

        while True:
            if self.token == '"':
                while True:
                    self.next_token()
                    if self.token == '"':
                        break
                    else:
                        val.append(self.token)
                if self.token == '"':
                    self.next_token()
                else:
                    raise NameError("\" missing")
            elif self.token == '{':
                brac_counter = 0
                while True:
                    self.next_token()
                    if self.token == '{':
                        brac_counter += 1
                    if self.token == '}':
                        brac_counter -= 1
                    if brac_counter < 0:
                        break
                    else:
                        val.append(self.token)
                if self.token == '}':
                    self.next_token()
                else:
                    raise NameError("} missing")
            elif self.token != "=" and re.match(u"\w|#|,", self.token):
                value = self.query_hashtable(self.token)
                val.append(value)
                while True:
                    self.next_token()
                    # if token is in hashtable then replace
                    value = self.query_hashtable(self.token)
                    if re.match(u"[^\w#]|,|}|{", self.token):  # self.token == '' :
                        break
                    else:
                        val.append(value)

            elif self.token.isdigit():
                value = self.token
                self.next_token()
            else:
                if self.token in self.hashtable:
                    value = self.hashtable[self.token]
                else:
                    value = self.token
                self.next_token()

            if re.match(u"}|,", self.token):
                break

        value = ' '.join(val)

        # PATCH!
        value = value.replace('\\ " ', '\\"')
        value = value.replace(' { ', '{')
        value = value.replace(' } ', '}')
        value = value.replace('{ ', '{')
        value = value.replace('} ', '}')
        value = value.replace(' {', '{')
        value = value.replace(' }', '}')

        return value

    def query_hashtable(self, s):
        if s in self.hashtable:
            return self.hashtable[self.token]
        else:
            return s

    def name(self):
        name = self.token
        self.next_token()
        return name

    def key(self):
        key = self.token
        self.next_token()
        return key

    def record(self):
        if self.token not in ['comment', 'string', 'preamble']:
            record_type = self.token
            self.next_token()
            if self.token == '{':
                self.next_token()
                key = self.key()
                self.records[key] = {}
                self.records[key]['ENTRYTYPE'] = str(record_type.lower())
                self.records[key]['ID'] = str(key)
                if self.token == ',':
                    while True:
                        self.next_token()
                        field = self.field()
                        if field:
                            k = str(field[0].lower())
                            val = field[1]

                            if k == 'page':
                                k = 'pages'

                            if k == 'pages':
                                val = val.replace('--', '-')

                            if k == 'title':
                                #   Preserve capitalization, as described in http://tex.stackexchange.com/questions/7288/preserving-capitalization-in-bibtex-titles
                                #   This will likely choke on nested curly-brackets, but that doesn't seem like an ordinary practice.
                                def capitalize(s):
                                    return s.group(1) + s.group(2).upper()
                                while val.find('{') > -1:
                                    caps = (val.find('{'), val.find('}'))
                                    val = val.replace(val[caps[0]:caps[1] + 1], re.sub("(^|\s)(\S)", capitalize, val[caps[0] + 1:caps[1]]).strip())

                            self.records[key][k] = val
                        if self.token != ',':
                            break
                    if self.token == '}':
                        pass
                    else:
                        # assume entity ended
                        if self.token == '@':
                            pass
                        else:
                            raise NameError("@ missing")
