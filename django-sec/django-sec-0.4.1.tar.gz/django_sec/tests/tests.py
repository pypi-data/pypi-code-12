from __future__ import print_function

import os
import datetime
from datetime import timedelta
import time
import socket
import threading
from functools import cmp_to_key

socket.gethostname = lambda: 'localhost'

import six

import django
from django.core.management import call_command
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

from django_sec import models
from django_sec import utils
from django_sec import constants as c

import warnings
warnings.simplefilter('error', RuntimeWarning)

class Tests(TestCase):
    
    #fixtures = ['test_jobs.json']
    
    def setUp(self):
        pass
    
    def test_unit(self):
        unit, _ = models.Unit.objects.get_or_create(name='U_iso4217USD')
        # In Django >= 1.9, you can't set a self-referential field during creation.
        unit.save()
        self.assertTrue(unit.true_unit)
        