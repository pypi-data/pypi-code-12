# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Interface for a collaborative group'''

from groupspace import IGroupSpace
from zope.container.constraints import contains

class ICollaborativeGroup(IGroupSpace):
    '''A collaborative group serves the needs of those working towards a common goal.'''
    contains('edrnsite.collaborations.interfaces.ICollaborativeGroupIndex')
