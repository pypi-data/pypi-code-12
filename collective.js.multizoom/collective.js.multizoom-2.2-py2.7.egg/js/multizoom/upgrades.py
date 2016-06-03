from Products.CMFCore.utils import getToolByName

def recook_js_resources(context):
    getToolByName(context, 'portal_javascripts').cookResources()

