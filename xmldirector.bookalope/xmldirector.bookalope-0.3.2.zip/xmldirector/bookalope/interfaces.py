# -*- coding: utf-8 -*-

################################################################
# xmldirector.bookalope
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from zope.interface import Interface
from zope import schema
from xmldirector.bookalope.i18n import MessageFactory as _


class IBrowserLayer(Interface):
    """A brower layer specific to my product """


class IBookalopeSettings(Interface):
    """ Bookalope settings """

    bookalope_api_key = schema.TextLine(
        title=_(u'Bookalope API key'),
        required=True
    )

    bookalope_beta = schema.Bool(
        title=_(u'Use Bookalope beta service'),
        default=False
    )
