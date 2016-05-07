import requests
import xmltodict


def convert_xml():
    r = requests.get('http://www.w3schools.com/xml/cd_catalog.xml')
    response = xmltodict.parse(r.text)
    ret = []
    for p in response['CATALOG']['CD']:
        ret.append(p['TITLE'])
    return ret


if __name__ == '__main__':
    print(convert_xml())
