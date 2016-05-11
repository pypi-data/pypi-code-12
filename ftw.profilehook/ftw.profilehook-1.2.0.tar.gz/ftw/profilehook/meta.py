from ftw.profilehook.interfaces import IBeforeImportHook
from ftw.profilehook.interfaces import IProfileHook
from zope.component import zcml
from zope.configuration.fields import GlobalObject
from zope.interface import Interface
import zope.schema


class IRegisterHook(Interface):
    """Register an upgrade step which imports a generic setup profile
    specific to this upgrade step.
    """

    profile = zope.schema.TextLine(
        title=u"GenericSetup profile id",
        required=True)

    handler = GlobalObject(
        title=u'Handler',
        description=u'',
        required=True)


def register_hook(context, profile, handler):
    return _register_hook_adapter(context,
                                  profile=profile,
                                  handler=handler,
                                  directive_name='profilehook:hook',
                                  providing=IProfileHook)


def register_before_import_hook(context, profile, handler):
    return _register_hook_adapter(context,
                                  profile=profile,
                                  handler=handler,
                                  directive_name='profilehook:before_import_hook',
                                  providing=IBeforeImportHook)


def _register_hook_adapter(context, profile, handler, directive_name, providing):
    def factory(site):
        return handler

    context.action(
        discriminator=(directive_name, profile),
        callable=zcml.handler,
        args=('registerAdapter',
              factory, [Interface], providing, profile, context.info))
