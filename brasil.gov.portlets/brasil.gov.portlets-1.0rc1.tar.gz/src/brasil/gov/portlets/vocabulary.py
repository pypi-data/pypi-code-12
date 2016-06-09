# -*- coding: utf-8 -*-
from plone import api
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class ImageScaleVocabulary(object):
    """ Create a vocabulary of image scales available in the site """

    def __call__(self, context):
        properties_tool = api.portal.get_tool(name='portal_properties')
        imagescales_properties = getattr(properties_tool, 'imaging_properties', None)
        raw_scales = getattr(imagescales_properties, 'allowed_sizes', None)

        image_scales = {}
        for line in raw_scales:
            line = line.strip()
            if line:
                splits = line.split(' ')
                if len(splits) == 2:
                    name = line
                    image_scales[name] = (splits[0], )
        return SimpleVocabulary.fromValues(image_scales)

ImageScaleVocabularyFactory = ImageScaleVocabulary()
