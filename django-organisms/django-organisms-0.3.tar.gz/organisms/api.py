from organisms.models import Organism

# Import and set logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

try:
    from tastypie.resources import ModelResource, ALL
except ImportError:
    logger.info('Not using django-tastypie in organisms/api.py file')
    quit()


class OrganismResource(ModelResource):

    class Meta:
        queryset = Organism.objects.all()
        filtering = {'scientific_name': ALL, 'slug': ALL,
                     'taxonomy_id': ALL}
        allowed_methods = ['get']
        detail_uri_name = 'slug'
