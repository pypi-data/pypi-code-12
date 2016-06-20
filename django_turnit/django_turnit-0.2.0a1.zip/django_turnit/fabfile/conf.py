# -*- coding: utf-8 -*-
"""
config for fabric

:creationdate: 09/03/16
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.fabfile.conf

"""
import os

__author__ = 'fguerin'
PROJECT_ROOT = os.path.join(os.getcwd(), '..')

PROJECT = {'docs_dir': os.path.join(PROJECT_ROOT, 'docs'),
           'src_dir': os.path.join(PROJECT_ROOT, 'django_turnit'),
           }
