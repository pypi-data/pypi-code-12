#!/usr/bin/env python

##  get_indexes_associated_with_fields.py
##  Avi Kak

##  Large database files may have hundreds of fields and it is not always easy to
##  figure out what numerical index is associated with a given field.

##  At the same time, the constructor of the DecisionTree module requires that the
##  field that holds the class label and fields that contain the feature values be
##  specified by their numerical zero-based indexes.

##  If you have a very large database and you are faced with the problem described
##  above, you can run this script to see the zero-based numerical index values
##  associated with the different columns of your CSV file.

##  CALL SYNTAX:    get_indexes_associated_with_fields.py    my_database_file.csv


import re
import sys
import string

if len( sys.argv ) != 2:                                          
    print "Call syntax:   get_indexes_associated_with_fields.py  filename.csv"
    sys.exit(1)  

def convert(value):
    try:
        answer = float(value)
        return answer
    except:
        return value

def cleanup_csv(line):
    line = line.translate(bytes.maketrans(b":?/()[]{}'",b"          ")) \
           if sys.version_info[0] == 3 else line.translate(string.maketrans(":?/()[]{}'","          "))
    double_quoted = re.findall(r'"[^\"]+"', line[line.find(',') : ])
    for item in double_quoted:
        clean = re.sub(r',', r'', item[1:-1].strip())
        parts = re.split(r'\s+', clean.strip())
        line = str.replace(line, item, '_'.join(parts))
    white_spaced = re.findall(r',(\s*[^,]+)(?=,|$)', line)
    for item in white_spaced:
        litem = item
        litem = re.sub(r'\s+', '_', litem)
        litem = re.sub(r'^\s*_|_\s*$', '', litem) 
        line = str.replace(line, "," + item, "," + litem) if line.endswith(item) else str.replace(line, "," + item + ",", "," + litem + ",") 
    fields = re.split(r',', line)
    newfields = []
    for field in fields:
        newfield = field.strip()
        if newfield == '':
            newfields.append('NA')
        else:
            newfields.append(newfield)
    line = ','.join(newfields)
    return line

training_datafile = sys.argv[1]
filein = open(training_datafile,"rU")
line = filein.readline()
record = cleanup_csv(line)
all_fields = record.strip().split(',')

dups = [x for x in all_fields if all_fields.count(x) > 1]
assert len(dups) == 0,  "\n\nYour training file is NOT usable --- it contains duplicate field names %s" % str(dups)

num_of_fields = len(all_fields)
print "\nNumber of fields: %d" % num_of_fields
all_fields_with_indexes = {k : all_fields[k] for k in range(num_of_fields)}
all_fields_with_indexes_inverted = {all_fields[j] : j for j in range(num_of_fields)}
print "\nAll field names along with their positional indexes: %s" % str(all_fields_with_indexes)
print "\n\nInverted index for field names:"
for key in sorted(all_fields_with_indexes_inverted, key=lambda x: x.lower()):
    print "%s=>%s  " % (key, all_fields_with_indexes_inverted[key]), 


