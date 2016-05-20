# -*- coding: utf-8 -*-

# zope imports
from Products.ATContentTypes import ATCTMessageFactory as ATMF
from collective.z3cform.widgets.enhancedtextlines import (
    EnhancedTextLinesFieldWidget,
)
from plone.app.textfield import RichText
from plone.app.textfield.widget import RichTextFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer

# local import
from ps.plone.mls import _, interfaces


class IFeaturedListings(model.Schema):
    """A list of featured MLS Listings."""

    directives.widget(listing_ids=EnhancedTextLinesFieldWidget)
    listing_ids = schema.List(
        description=_(u'Add one Listing ID for each entry to show up.'),
        title=_(u'MLS Listing IDs'),
        unique=True,
        value_type=schema.TextLine(
            title=_(u'ID'),
        ),
    )

    directives.widget(body_text=RichTextFieldWidget)
    body_text = RichText(
        required=False,
        title=ATMF(u'label_body_text', default=u'Body Text'),
    )


@implementer(
    IFeaturedListings,
    interfaces.IListingTraversable,
)
class FeaturedListings(Item):
    """A list of featured MLS Listings."""
