from pylib import views
from pylib.views import FalconAbstraction
from pylib.validation import schemas
from pylib.misc import dictutils, functions


class Collection(FalconAbstraction):
    """FalconAbstraction alias for collection of entities.

    It will handle cs(create, search) requests on the collection url.
    """

    def __init__(self, path, schema, before=[], after=[]):
        super().__init__(path, schema, before, after)


def search(collection, before=[], after=[]):
    """Register a function to handle GET requests on the collection.

    The function takes one required parameter `query` and kwargs parameter.
    It should return an a list of entities or an empty list.
    e.g.
        def search_for_patient(query, query_type, user, **kwargs):
            return dict(name='')
    """

    def decorator(f):
        def find(resource, request, response, **kwargs):
            query = request.get_param('query')

            entities = f(query, **dictutils.merge_dict(kwargs, request.context))
            views.response(response, collection.schema, entities, many=True)

        all_before = collection.before + before
        all_after = collection.after + after
        find = views.setup_hooks(find, all_before, all_after)
        functions.attach_method(find, collection.resource, 'on_get')
        return f
    return decorator


def create(collection, before=[], after=[]):
    """Register a function to handle POST requests on the collection.

    The function takes a single parameter `entity` that is validated
    using the collection's schema and kwargs parameter.
    It returns the id of the new entity. Due to this the id field must
    exist in the schema
    e.g.
        def create_patient(patient, user, **kwargs):
            return dict(hospital_id=user['hospital_id'], **patient)
    """
    def decorator(f):
        def new(resource, request, response, **kwargs):
            entity = dict(request.params)
            entity = schemas.load(collection.schema, entity)

            entity_id = f(entity, **dictutils.merge_dict(kwargs, request.context))
            views.response(response, collection.schema, dict(id=entity_id))

        all_before = collection.before + before
        all_after = collection.after + after
        new = views.setup_hooks(new, all_before, all_after)
        functions.attach_method(new, collection.resource, 'on_post')
        return f
    return decorator
