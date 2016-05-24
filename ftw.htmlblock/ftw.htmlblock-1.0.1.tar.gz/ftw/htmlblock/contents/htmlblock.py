from ftw.htmlblock import _
from ftw.htmlblock.contents.interfaces import IHtmlBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IHtmlBlockSchema(form.Schema):
    """HTML block for simplelayout
    """

    title = schema.TextLine(
        title=_(u'htmlblock_title_label', default=u'Title'),
        required=True,
    )

    show_title = schema.Bool(
        title=_(u'htmlblock_show_title_label', default=u'Show title'),
        default=False,
        required=False,
    )

    content = schema.Text(
        title=_(u'htmlblock_content_label', default=u'Content'),
        description=_(u'htmlblock_content_description',
                      default=u'The content will be rendered without '
                              u'being escaped.'),
        required=False,
    )

    form.order_before(title='*')

alsoProvides(IHtmlBlockSchema, IFormFieldProvider)


class HtmlBlock(Item):
    implements(IHtmlBlock)
