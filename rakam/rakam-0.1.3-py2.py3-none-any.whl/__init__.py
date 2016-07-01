# -*- coding: utf-8 -*-
"""
    Rakam client for limited use.
    Project is only made for use in multiple internal projects, hence it only
    contains a small amount of functionality.
"""


__version__ = '0.1.3'
__author__ = 'Kaan Uğurlu'
__contact__ = 'kugurlu94@gmail.com'
__all__ = ['RakamClient', 'RakamCredentials']


from rakam.connection import RakamCredentials
from rakam.client import RakamClient
