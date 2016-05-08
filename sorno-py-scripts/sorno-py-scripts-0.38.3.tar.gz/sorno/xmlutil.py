from __future__ import print_function

from xml.dom import minidom

def prettify(xml_str, indent=2):
    parsed = minidom.parseString(xml_str)
    return parsed.toprettyxml(indent=" " * indent)

if __name__ == '__main__':
    print(
        prettify("<fruits><fruit>apple</fruit><fruit>orange</fruit></fruits>")
    )
