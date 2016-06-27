from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from copy import deepcopy
from datetime import datetime
from ftw.servicenavigation.form import ANNOTATION_KEY
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.viewlets import ViewletBase
from plone.memoize import ram
from zope.annotation import IAnnotations


def _render_links_cachkey(method, self):
    storage, nav_root = self.get_storage()
    nav_root_path = '/'.join(nav_root.getPhysicalPath())
    storage_modified = storage.get('modified', datetime.now())
    portal_url = api.portal.get().absolute_url()

    return (nav_root_path, storage_modified, portal_url)


class ServiceNavigation(ViewletBase):

    @ram.cache(_render_links_cachkey)
    def get_service_links(self):
        links = []
        storage, nav_root = self.get_storage()

        if storage.get('disable', False):
            return []

        for link in storage.get('links', []):
            links.append(
                dict(label=link['label'],
                     icon=link['icon'],
                     url=self.get_link(link)))

        return links

    def get_link(self, link):
        internal_link = link['internal_link']
        external_link = link['external_url']

        if internal_link:
            internal_link = api.portal.get().unrestrictedTraverse(
                internal_link.lstrip('/'))
            if internal_link:
                internal_link = internal_link.absolute_url()

        return external_link or internal_link

    def get_storage(self):
        storage = None
        nav_root = api.portal.get_navigation_root(self.context)
        while True:
            annotations = IAnnotations(nav_root)
            storage = deepcopy(annotations.get(ANNOTATION_KEY, {}))

            if IPloneSiteRoot.providedBy(nav_root):
                break
            elif storage.get('disable', False):
                break
            elif storage.get('links', []):
                break
            else:
                nav_root = api.portal.get_navigation_root(
                    aq_parent(aq_inner(nav_root))
                )
        return storage, nav_root

    def can_modify(self):
        context_state = self.context.restrictedTraverse(
            '@@plone_context_state'
        )
        if not INavigationRoot.providedBy(context_state.canonical_object()):
            return False

        return api.user.has_permission(
            'ftw.servicenavigation: Modify Service Navigation',
            obj=self.context
        )

    def edit_url(self):
        return '{0}/service_navigation_form'.format(
            api.portal.get_navigation_root(self.context).absolute_url()
        )
