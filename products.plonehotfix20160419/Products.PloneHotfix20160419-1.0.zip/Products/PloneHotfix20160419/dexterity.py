try:
    from Products.CMFPlone import patches  # noqa
except ImportError:
    pass
try:
    from AccessControl.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass
from Products.CMFCore import permissions
try:
    from AccessControl.security import _getSecurity
except ImportError:
    from Products.Five.security import _getSecurity
try:
    from plone.dexterity.filerepresentation import DAVResourceMixin
    from plone.dexterity.filerepresentation import DAVCollectionMixin
    from plone.dexterity.filerepresentation import FolderDataResource
except ImportError:
    DAVResourceMixin = None

if DAVResourceMixin is not None:
    read_methods = (
        'get_size',
        'content_type',
        'Format',
        'manage_DAVget',
        'manage_FTPget',
    )

    security = _getSecurity(DAVResourceMixin)
    security.declareProtected(permissions.View, *read_methods)
    security.declareProtected(permissions.ModifyPortalContent, 'PUT')
    InitializeClass(DAVResourceMixin)

    security = _getSecurity(DAVCollectionMixin)
    security.declareProtected(
        permissions.AddPortalContent, 'PUT_factory', 'MKCOL_handler')
    security.declareProtected(permissions.ListFolderContents, 'listDAVObjects')
    InitializeClass(DAVCollectionMixin)

    read_methods = (
        'HEAD',
        'TRACE',
        'PROPFIND',
        'manage_DAVget',
        'manage_FTPget'
    )

    write_methods = (
        'PROPPATCH',
        'LOCK',
        'UNLOCK',
        'PUT'
    )
    security = _getSecurity(FolderDataResource)
    security.declareProtected(permissions.View, *read_methods)
    security.declareProtected(permissions.ModifyPortalContent, *write_methods)
    security.declareProtected(permissions.AddPortalContent, 'MOVE', 'COPY')
    security.declareProtected(
        permissions.ListFolderContents, 'OPTIONS', 'listDAVObjects')
    security.declareProtected(permissions.DeleteObjects, 'DELETE')
    InitializeClass(FolderDataResource)
