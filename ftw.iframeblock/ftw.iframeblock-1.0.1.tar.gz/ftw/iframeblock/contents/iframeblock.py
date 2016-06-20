from ftw.iframeblock import _
from ftw.iframeblock.contents.interfaces import IIFrameBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IIFrameBlockSchema(form.Schema):
    """iFrame block for simplelayout
    """

    url = schema.URI(
        title=_(u'iframeblock_url_label', default=u'URL'),
        required=True,
        description=_(u'iframeblock_url_desc', default=u'The given site must '
                      'have the <a href="https://github.com/davidjbradshaw/'
                      'iframe-resizer" target="_blank">iframe-resizer package'
                      '</a> installed.<br>Without this package, the auto '
                      'resize WONT work!')
    )

    height = schema.Int(
        title=_(u'iframeblock_height_label', default=u'Height'),
        default=400,
        required=False,
    )

    auto_size = schema.Bool(
        title=_(u'iframeblock_auto_size_label', default=u'Auto Size'),
        default=False,
        description=_(u'iframeblock_auto_size_desc', default=u'When auto '
                      'resize is set, the value of the "Height" field '
                      'wont have any influence on how the block is'
                      ' displayed.'),
        )

alsoProvides(IIFrameBlockSchema, IFormFieldProvider)


class IFrameBlock(Item):
    implements(IIFrameBlock)
