#!/usr/bin/env python
# you'll need to install requests to make this example work
# pip install --upgrade requests
# should do the trick
import requests
import json

# point the client to your own py3o.fusion server
url = 'http://localhost:8765/form'

# target formats you want... can be odt, pdf, doc, docx
targetformats = ["pdf"]


class MyEncoder1(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Item):
            obj = obj._asdict()
        else:
            obj = super(MyEncoder1, self).default(obj)

        return obj


class Item(object):
    def _asdict(self):
        return self.__dict__


document = Item()
document.person_name = 'Aide'
document.person_surname = 'Florent'
document.person_company = "XCG Consulting"
document.person_url = "http://www.xcg-consulting.fr"

data = {
    "document": document
}

data_s = json.dumps(data, cls=MyEncoder1)

for targetformat in targetformats:
    # open the files you need
    files = {
        'tmpl_file': open('templates/fusion2pdf.odt', 'rb'),
    }

    # fusion API needs those 3 keys
    fields = {
        "targetformat": targetformat,
        "datadict": data_s,
        "image_mapping": "{}",
    }

    # and it needs to receive a POST with fields and files
    r = requests.post(url, data=fields, files=files)
    files['tmpl_file'].close()

    # TODO: handle error codes
    if r.status_code == 400:
        # server says we have a problem...
        # let's give the info back to our human friend
        print r.json()

    else:
        chunk_size = 1024
        # fusion server will stream an ODT file content back
        ext = targetformat.lower()
        with open('fusion2pdf.%s' % ext, 'wb') as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
