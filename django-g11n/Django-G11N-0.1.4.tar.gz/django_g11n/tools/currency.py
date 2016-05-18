"""
Fetch Currency data, ISO 4217
"""
from io import StringIO
from xml.etree import ElementTree
import requests

URL = "http://www.currency-iso.org/dam/downloads/lists/list_one.xml"

ADDITIONS = [
  ['Palestine, State of',
   '376', 'New Israeli Sheqel', 'ILS', '2', False, True, False],

  ['South Georgia and the South Sandwich Islands',
   '826', 'Pound Sterling', 'GBP', '2', False, True, False]]

DEFAULTS_OVERRIDE = {'BHUTAN':'BTN',
                     'BOLIVIA (PLURINATIONAL STATE OF)':'BOB',
                     'CHILE':'CLP',
                     'COLOMBIA':'COP',
                     'CUBA':'CUP',
                     'EL SALVADOR':'USD',
                     'HAITI':'HTG',
                     'LESOTHO':'LSL',
                     'MEXICO':'MXN',
                     'NAMIBIA':'NAD',
                     'PANAMA':'USD',
                     'SWITZERLAND':'CHF',
                     'UNITED STATES OF AMERICA (THE)':'USD',
                     'URUGUAY':'UYU'}

def get(url=URL):
    """Fetch currency and parse it.
    Yields per yield:
    - iso_short_name_lower_case
    - currency_numeric
    - currency_name
    - currency_cod,
    - is_fund
    - default
    - boolean if this is an ISO 4217 entry (False if it is an local override)
    All fields are text fields, the iso_short_name_lower_case is all upper case
    due to the source document.
    """
    response = requests.get(url)
    response.encoding = 'UTF-8'
    xml = StringIO()
    xml.write(response.text)

    xml.seek(0)
    tree = ElementTree.parse(xml)

    for entry in tree.getiterator():
        if entry.tag != 'CcyNtry':
            continue

        items = ['CtryNm', 'CcyNbr', 'CcyNm', 'Ccy', 'CcyMnrUnts']
        tmp = list()
        empty = False
        is_fund = False
        for item in items:
            element = entry.find(item)
            if element is None:
                empty = True
                element = ''
            else:
                if item == 'CcyNm':
                    if element.get('IsFund') is not None:
                        is_fund=True
                data = element.text.strip()
                data = data.replace('’', "'")
                data = data.replace('’', "'")

            tmp.append(data)
        tmp.append(is_fund)
        tmp.append(True)

        if tmp[0] in DEFAULTS_OVERRIDE:
            if tmp[3] != DEFAULTS_OVERRIDE[tmp[0]]:
                tmp[-1] = False

        # Make ZZ type currencies non-default
        if tmp[0][:2] == 'ZZ' and tmp[0][2:4].isdigit():
            tmp[-1] = False

        if not empty:
            tmp.append(True)
            yield tmp

        for item in ADDITIONS:
            yield item

