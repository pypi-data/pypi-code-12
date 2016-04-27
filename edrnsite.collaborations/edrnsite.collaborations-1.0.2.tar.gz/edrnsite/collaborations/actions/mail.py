# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Mailing action for content rules for the EDRN Site Collaborations.'''

from Acquisition import aq_inner
from plone.app.contentrules.actions.mail import IMailAction, MailAction, MailActionExecutor, MailAddForm, MailEditForm
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements, Interface
import socket, smtplib

class IEDRNSiteCollaborationsMailAction(IMailAction):
    '''EDRN Site Collaborations mail action.'''

class EDRNSiteCollaborationsMailAction(MailAction):
    '''EDRN Site Collaborations mail action, which is just like the regular Plone mail action, except that it ignores errors
    when sending mail, and makes sure the collaborative group it's sending email about actually wants update notifications.'''
    implements(IEDRNSiteCollaborationsMailAction)
    element = 'edrn.actions.CollaborationsMail'

class EDRNSiteCollaborationsMailActionExecutor(MailActionExecutor):
    '''Executor that actually sends email (ignoring errors) for an EDRN Collaborative Group, and only
    if the group has notifications enabled.'''
    adapts(Interface, IEDRNSiteCollaborationsMailAction, Interface)
    def __call__(self):
        try:
            context = aq_inner(self.context)
            mtool = getToolByName(context, 'portal_membership')
            if mtool.isAnonymousUser():
                # This should never happen unless someone gives Anonymous edit permissions
                return
            updateNotifications = getattr(context, 'updateNotifications', False)
            if updateNotifications:
                return super(EDRNSiteCollaborationsMailActionExecutor, self).__call__()
            return True
        except (socket.error, smtplib.SMTPException):
            return True

class EDRNSiteCollaborationsMailAddForm(MailAddForm):
    '''Form to show when adding an EDRN Site Collaborations mail action.'''
    form_fields = form.FormFields(IEDRNSiteCollaborationsMailAction)
    label = _(u'Add EDRN Collaborations Mail Action')
    description = _(u'A mail action that sends email for collaborative groups, and ignores transmission errors.')
    form_name = _(u'Configure EDRN Site Collaborations element')
    def create(self, data):
        a = EDRNSiteCollaborationsMailAction()
        form.applyChanges(a, self.form_fields, data)
        return a
        
class EDRNSiteCollaborationsMailEditForm(MailEditForm):
    '''Form to show when editing an EDRN Site Collaborations mail action.'''
    form_fields = form.FormFields(IEDRNSiteCollaborationsMailAction)
    label = _(u'Edit EDRN Collaborations Mail Action')
    description = _(u'A mail action for EDRN collaborative groups that ignores transmission errors.')
    form_name = _(u'Configure EDRN Site Collaborations element')
