# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.portlets.browser.manage import ManageContextualPortlets
from zope.component import getMultiAdapter

from ftw.footer import _


class CustomManageContextualPortlets(ManageContextualPortlets):

    def set_blacklist_status(self, manager, group_status, content_type_status,
                             context_status):
        """Stay on the same page rather then redirecting to the portlet
        management view.
        """
        superclass = super(CustomManageContextualPortlets, self)
        superclass.set_blacklist_status(
            manager, group_status, content_type_status, context_status
        )

        # Give some feedback to the user, otherwise he might miss the fact
        # that the form has been submitted.
        messages = IStatusMessage(self.request)
        messages.add(text=_(u'Settings have been saved.'), type=u'success')

        base_url = str(
            getMultiAdapter((self.context, self.request), name='absolute_url')
        )

        if self.request.get('HTTP_REFERER', '').endswith('manage-footer'):
            # This is the part we need to override from the parent class.
            self.request.response.redirect(base_url + '/manage-footer')
        else:
            self.request.response.redirect(base_url + '/@@manage-portlets')

        return ''
