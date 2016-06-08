#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Import departements and towns from csv file
"""

DELIMITER = ","
QUOTECHAR = '"'

import sys
import csv
sys.path.append('.')

from django.core.management import setup_environ
import settings

setup_environ(settings)

from optparse import OptionParser

from ishtar_common import models

def insert_department(value):
    idx, label = value
    if models.Department.objects.filter(number=idx).count():
        return
    models.Department(number=idx, label=label).save()
    print idx, label, u" inserted"

def insert_town(value):
    idx, label = value
    if models.Town.objects.filter(numero_insee=idx).count():
        return
    try:
        dpt = models.Department.objects.get(number=idx[:2])
    except:
        return
    models.Town(numero_insee=idx, name=label, departement=dpt).save()
    print idx, label, u" inserted"

tables = {u"department":insert_department,
          u"town":insert_town}

usage = u"usage: %%prog csv_file.csv table_name\n\n"\
        u"Table name must be in: %s." % u", ".join(tables.keys())
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

try:
    assert len(args) == 2
except AssertionError:
    parser.error(u"You must provide one csv file and the table name.")

try:
    assert args[1] in tables.keys()
except AssertionError:
    parser.error(u"Incorrect table name.")

try:
    values = csv.reader(open(args[0], 'rb'), delimiter=DELIMITER,
                    quotechar=QUOTECHAR)
except (IOError):
    parser.error(u"Incorrect CSV file.")

for value in values:
    tables[args[1]](value)
