from Products.CMFCore.utils import getToolByName


def uninstall(portal, reinstall=False):
    if reinstall:
        return
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-Products.Doormat:uninstall')
    return "Ran all uninstall steps."
