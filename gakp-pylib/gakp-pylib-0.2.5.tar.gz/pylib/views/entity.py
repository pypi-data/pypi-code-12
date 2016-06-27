from pylib import views
from pylib.views import FalconAbstraction
from pylib.validation import schemas
from pylib.misc import dictutils, functions


class Entity(FalconAbstraction):
    """FalconAbstraction alias for a single entity.

    It'll handle rud(read, update, delete) requests on the entity
    the url.

    Args:
        idname (str): Name of the parameter that represents the id of
            the entity from the request.
    """

    def __init__(self, path, idname, schema, before=[], after=[]):
        super().__init__(path, schema, before, after)
        self.path = '%s/{%s}' % (path, idname)
        self.idname = idname


def read(entity, before=[], after=[]):
    """Register a function to handle GET requests on specific resources.

    The function takes a single parameter named after the collection's
    `id_name` property and kwargs parameter. It returns the entity.
    e.g.
        def get_patient(pid, **kwargs):
            return patients[pid]
    """
    def decorator(f):
        def get(resource, request, response, **kwargs):
            entity_id = kwargs.pop(entity.idname)
            read_entity = f(entity_id, **dictutils.merge_dict(kwargs, request.context))
            views.response(response, entity.schema, read_entity)

        all_before = entity.before + before
        all_after = entity.after + after
        get = views.setup_hooks(get, all_before, all_after)
        functions.attach_method(get, entity.resource, 'on_get')
        return f
    return decorator


def update(entity, before=[], after=[]):
    """Register a function to handle PUT requests on specific resources.

    The function takes two parameters with one named after the collection's
    `id_name` property, the `entity` and kwargs parameter.
    It returns the new entity.
    e.g.
        def edit_patient(pid, new_patient, **kwargs):
            patient = patients[pid]
            patient.update(new_patient)
            return patient
    """
    def decorator(f):
        def edit(resource, request, response, **kwargs):
            entity_id = kwargs.pop(entity.idname)
            req_entity = dict(request.params)
            req_entity = schemas.load(entity.schema, req_entity)

            new_entity = f(entity_id, req_entity, **dictutils.merge_dict(kwargs, request.context))
            views.response(response, entity.schema, new_entity)

        all_before = entity.before + before
        all_after = entity.after + after
        edit = views.setup_hooks(edit, all_before, all_after)
        functions.attach_method(edit, entity.resource, 'on_put')
        return f
    return decorator


def delete(entity, before=[], after=[]):
    """Register a function to handle DELETE requests on specific resources.

    The function takes a single parameter named after the collection's
    `id_name` property and kwargs parameter.It returns the deleted entity.
    e.g.
        def delete_patient(pid, new_patient, **kwargs):
            return patients.pop(pid)
    """
    def decorator(f):
        def remove(resource, request, response, **kwargs):
            entity_id = kwargs.pop(entity.idname)
            old_entity = f(entity_id, **dictutils.merge_dict(kwargs, request.context))
            views.response(response, entity.schema, old_entity)

        all_before = entity.before + before
        all_after = entity.after + after
        remove = views.setup_hooks(remove, all_before, all_after)
        functions.attach_method(remove, entity.resource, 'on_delete')
        return f
    return decorator
