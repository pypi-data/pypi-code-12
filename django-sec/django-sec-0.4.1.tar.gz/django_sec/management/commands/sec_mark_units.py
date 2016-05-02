from __future__ import print_function

import urllib
import os
import re
import sys
from zipfile import ZipFile
import time
from datetime import date, datetime, timedelta
from optparse import make_option
from StringIO import StringIO
import traceback
import random
from multiprocessing import Process, Lock, Queue
import collections

from django.core.management.base import NoArgsCommand, BaseCommand
from django.db import transaction, connection, IntegrityError, DatabaseError
from django.db.models import Q, F
from django.conf import settings
from django.utils import timezone

from django_sec import models
from django_sec.models import DATA_DIR, c

try:
    from psycopg2.extensions import TransactionRollbackError
except ImportError:
    TransactionRollbackError = Exception

try:
    from chroniker.models import Job
except ImportError:
    Job = None

class Command(BaseCommand):
    help = "Links duplicate units to the true canonical unit."
    args = ''
    option_list = BaseCommand.option_list + (
        make_option('--name',
            default=None),
    )
    
    def handle(self, **options):
        
        settings.DEBUG = False
        
        only_name = options['name']
        
        qs = models.Unit.objects.all()
        if only_name:
            qs = qs.filter(name__icontains=only_name)
        total = qs.count()
        i = 0
        dups = set()

        # Link all singular to plurals.
        qs = models.Unit.objects.filter(master=True)
        total = qs.count()
        i = 0
        for r in qs.iterator():
            i += 1
            sys.stdout.write('\r%i of %i' % (i, total))
            sys.stdout.flush()
            
            plural_qs = models.Unit.objects.filter(master=True).filter(Q(name=r.name+'s')|Q(name=r.name+'es')).exclude(id=r.id)
            if plural_qs.exists():
                models.Unit.objects.filter(true_unit=r).update(true_unit=plural_qs[0], master=False)
                r.true_unit = plural_qs[0]
                r.master = False
                r.save()

        print()       
        print('%i duplicates linked' % len(dups)
        