# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Site Collaborations: collaborative group view
'''

from groupspace import GroupSpaceView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class CollaborativeGroupView(GroupSpaceView):
    '''Default view for a Collaborative Group.'''
    index = ViewPageTemplateFile('templates/collaborativegroup.pt')
