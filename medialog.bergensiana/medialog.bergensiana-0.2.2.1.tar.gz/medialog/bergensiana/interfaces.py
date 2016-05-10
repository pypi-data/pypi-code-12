from plone.theme.interfaces import IDefaultPloneLayer
    
from z3c.form import interfaces
from zope import schema
from zope.interface import alsoProvides
from plone.directives import form
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider
from zope.i18nmessageid import MessageFactory
from plone.app.portlets.interfaces import IColumn

_ = MessageFactory('medialog.bergensiana')


class IBergensianaLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer and a plone skin
       marker.
    """

class ITopper(IColumn):
    """The  topper
    Normally, you will register portlets for IColumn instead.
    """

class IAbove(IColumn):
    """here we put the above content portlets
    Normally, you will register portlets for IColumn instead.
    """    


class IBergensianaSettings(form.Schema):
	"""Adds settings to medialog.controlpanel
	"""

	form.fieldset(
		'Begensiana',
		label=_(u'Bergensiana'),
		fields=[
			'facebook',
			'instagram',
			'email',
			'twitter',
			'map',	
			'footertext',
			'phone',
			'contacttitle',
			'contacttext',
			'cssfile',
			'rulefile',
		],
	)

	facebook = schema.URI(
		title=_(u"label_facebook", default=u"Facebook"),
		description=_(u"help_facebook",
		default=u"URL to facebook account"),
		required=False,
	)

	instagram = schema.URI(
		title=_(u"label_instagram", default=u"Instagram"),
		description=_(u"help_instagram",
		default=u"URL to instagram"),
		required=False,
	)

	email = schema.TextLine(
		title=_(u"label_email", default=u"E-mail"),
		description=_(u"help_email",
		default=u""),
		required=False,
	)

	phone = schema.TextLine(
		title=_(u"label_phone", default=u"Phone"),
		description=_(u"help_phone",
		default=u""),
		required=False,
	)
	
	twitter = schema.URI(
		title=_(u"label_twitter", default=u"Twitter"),
		description=_(u"help_twitter",
		default=u"URL to twitter account"),
		required=False,
	)

	map = schema.URI(
		title=_(u"label_googlemap", default=u"Googlemap"),
		description=_(u"help_googlemap",
		default=u"URL to googlemap"),
		required=False,
	)

	footertext = schema.Text(
		title=_(u"label_footertext", default=u"Footertext"),
		description=_(u"help_footertext",
		default=u"Text for custom footer"),
		required=False,
	)

	contacttitle = schema.TextLine(
		title=_(u"label_contacttitle", default=u"Contact Title"),
		description=_(u"help_contacttitle",
		default=u"Contact Title"),
		required=False,
	)
	
	contacttext = schema.Text(
		title=_(u"label_contacttext", default=u"Contacttext"),
		description=_(u"help_contacttext",
		default=u"Text for contact us section"),
		required=False,
	)

	cssfile = schema.Choice(
	values=['compiled', 
            'blue', 
            'blue2',
            'slick',
            'stub',
            'k2',
            'orange', 
            'yellow',
            'white'],
        	required=False, 		
        )

	rulefile = schema.Choice(
            title=_(u"Rules file"),
            values=['a', 
            		'b',
            		'f',
            		'm',
            		'x'],
            required=False,
        )

alsoProvides(IBergensianaSettings, IMedialogControlpanelSettingsProvider)