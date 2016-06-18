# -*- coding: utf-8 -*-

"""
Created on 2016-06-18
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from zope.interface import implements

from kotti_google_analytics import _

