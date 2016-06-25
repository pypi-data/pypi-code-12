# -*- coding:utf-8 -*-
import os
import sys

# GENERAL
abspath = lambda *p: os.path.abspath(os.path.join(*p))
CONFIG_DIR = abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.dirname(CONFIG_DIR)
PROJECT_ROOT = os.path.dirname(CONFIG_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "apus"))

# DATABASE
DATABASE_NAME = 'apus.db'

# Usuário default
USERNAME = 'geislor'
FIRST_NAME = 'Geislor'
LAST_NAME = 'Crestani'
EMAIL = 'geislor@gmail.com'
