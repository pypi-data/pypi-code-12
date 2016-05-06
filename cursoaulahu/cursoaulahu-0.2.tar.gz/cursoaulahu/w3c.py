import requests
import xmltodict


def convert_xml(url):
    r = requests.get(url)
    response = xmltodict.parse(r.text)
    for p in response['CATALOG']['CD']:
        print(p['TITLE'])


if __name__ == '__main__':
    convert_xml('http://www.w3schools.com/xml/cd_catalog.xml')
