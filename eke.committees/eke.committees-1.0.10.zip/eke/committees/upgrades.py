# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

PROFILE_ID = 'profile-eke.committees:default'

def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''

def reloadTypes4to5(setupTool):
    '''Reload types.'''
    setupTool.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
