import os
import shutil
import sys
from zipfile import ZipFile, ZIP_DEFLATED

rpl_lst = [
    ('adminact_associated_file_general_contractor_attached_to_name',
     'adminact_associated_file_corporation_general_contractor_name'),
    ('adminact_associated_file_general_contractor_'
     'attached_to_address',
     'adminact_associated_file_corporation_general_contractor_'
     'address'),
    ('adminact_associated_file_general_contractor_'
     'address_complement',
     'adminact_associated_file_corporation_general_contractor_'
     'address_complement '),
    ('adminact_associated_file_general_contractor_'
     'attached_to_postal_code',
     'adminact_associated_file_corporation_general_contractor_'
     'postal_code '),
    ('adminact_associated_file_general_contractor_attached_to_town',
     'adminact_associated_file_corporation_general_contractor_town',
     ),
    ('adminact_associated_file_address',
     'adminact_associated_file_get_locality',
     )
]

context = dict(rpl_lst)


def value_replace(content):
    value = content
    modified = False
    for key in context:
        if key in value:
            modified = True
            value = value.replace(key, context[key])
    return value, modified


def replace(directory, infile):
    print("Processing {}".format(infile))
    outfile = "PREPROCESS--" + infile
    infile = directory + os.sep + infile
    outfile = directory + os.sep + outfile

    inzip = ZipFile(infile, 'r', ZIP_DEFLATED)
    outzip = ZipFile(outfile, 'w', ZIP_DEFLATED)

    values = {}
    idx = 0
    for xml_file in ('content.xml', 'styles.xml'):
        content = inzip.read(xml_file)
        values[xml_file], modified = value_replace(content)
        if modified:
            idx += 1

    for f in inzip.infolist():
        if f.filename in values:
            outzip.writestr(f.filename, values[f.filename])
        else:
            outzip.writestr(f, inzip.read(f.filename))

    inzip.close()
    outzip.close()
    # replace original by PREPROCESS
    shutil.move(outfile, infile)
    return idx

directory = sys.argv[-1]
idx = 0


for fle in os.listdir(directory):
    if fle.endswith('.odt'):
        idx += replace(directory, fle)

print("{} modifications".format(idx))
