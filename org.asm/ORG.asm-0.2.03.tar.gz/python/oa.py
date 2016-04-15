#!/usr/local/bin/python3.4
'''
orgasm -- shortdesc

orgasm is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2014 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import pkgutil
import argparse
import logging
import json


from orgasm.version import version
from orgasm.apps.config import getConfiguration     # @UnresolvedImport

__all__ = []
__version__ = version
__date__ = '2014-09-28'
__updated__ = '2014-09-28'
root_config_name='orgasm'

default_config = { 'software'       : "The Organelle Assembler",
                   'log'            : False,
                   'loglevel'       : 'INFO',
                   'outputfilename' : None,
                   'back'           : None,
                   'seeds'          : None,
                   'seedmincov'     : 1,
                   'kup'            : None,
                   'identity'       : 0.5,
                   'minlink'        : 5,
                   'version'        : False,
                   'progress'       : True
                }

DEBUG = 1
TESTRUN = 0
PROFILE = 0


if __name__ =="__main__":
    
    config = getConfiguration(root_config_name,
                              default_config)    
                
    if config[root_config_name]['outputfilename'] is None:
        config[root_config_name]['outputfilename']=config[root_config_name]['indexfilename']

    config[root_config_name]['module'].run(config)

    