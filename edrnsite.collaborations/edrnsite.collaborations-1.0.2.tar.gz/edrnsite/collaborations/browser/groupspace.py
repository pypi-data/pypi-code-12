# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Site Collaborations: group space view
'''

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class GroupSpaceView(BrowserView):
    '''Default view for a Group Space.'''
    index = ViewPageTemplateFile('templates/groupspace.pt')
