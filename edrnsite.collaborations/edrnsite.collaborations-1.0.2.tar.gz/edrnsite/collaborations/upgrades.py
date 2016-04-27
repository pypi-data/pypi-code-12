# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

_profileID = 'profile-edrnsite.collaborations:default'

def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''

def update1To2Types(setupTool):
    '''Update types in this profile version'''
    # FIXME: Collaborative Group Event got renamed to Group Event
    # If any are left in the portal we need to migrate them
    setupTool.runImportStepFromProfile(_profileID, 'contentrules')
    setupTool.runImportStepFromProfile(_profileID, 'types')
    setupTool.runImportStepFromProfile(_profileID, 'factorytool')
    setupTool.runImportStepFromProfile(_profileID, 'rolemap')
