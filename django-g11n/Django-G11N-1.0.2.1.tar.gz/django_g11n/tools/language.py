'''
Created on 9 May 2016

@author: martin
'''
import requests

URL = 'http://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt'
# From the source, the following description:
# These files may be used to download the list of language codes with their
# language names, for example into a database. To read the files, please note
# that one line of text contains one entry. An alpha-3 (bibliographic) code,
# an alpha-3 (terminologic) code (when given), an alpha-2 code (when given),
# an English name, and a French name of a language are all separated by pipe (|)
# characters. If one of these elements is not applicable to the entry, the field
# is left empty, i.e., a pipe (|) character immediately follows the preceding
# entry. The Line terminator is the LF character.
ADDITIONS = []

def get(url=URL):
    """Fetch Languages and parse it, yields an array with:
    - bibliographic code
    - terminologic code
    - alpha-2 code
    - Name in English
    - Name in French.
    - ISO-639-2 boolean (False if it is a local addition)
    """
    response = requests.get(url)
    response.encoding = 'UTF-8'
    text = response.text[::]
    if text.startswith('\ufeff'):
        text = text[1:]

    for line in text.split('\n'):
        row = line.split('|')
        row.append(True)
        yield row

    for row in ADDITIONS:
        yield row

    