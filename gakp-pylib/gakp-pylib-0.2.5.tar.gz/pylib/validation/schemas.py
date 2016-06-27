from pylib.misc import dictutils, functions
from pylib.validation.fields import DateTime, ObjectID

from falcon import HTTPBadRequest
from marshmallow import Schema
from marshmallow.fields import Int


class BaseSchema(Schema):
    id = Int(dump_only=True)
    createdat = DateTime(read_only=True, missing=DateTime.now_str)


class MongoSchema(Schema):
    id = ObjectID(dump_only=True)
    _id = ObjectID(dump_to='id', dump_only=True)
    createdat = DateTime(read_only=True, missing=DateTime.now_str)


def error_map_to_string(error_map):
    error_list = []
    for item in dictutils.dict_items(error_map):
        key, value = item
        if isinstance(value, dict):
            error_list.extend(error_map_to_string(value))
        else:
            error_list.append('%s: %s' % (key, value[0]))
    return error_list


def get_top_error(errors, many):
    if many:
        # get first error in list of many
        _, entity = functions.first(dictutils.dict_items(errors))
        error_list = error_map_to_string(entity)
        return functions.first(error_list)
    else:
        error_list = error_map_to_string(errors)
        return functions.first(error_list)


def load(schema, obj, many=False):
    """Deserialize the object passed using the given schema

    The object is validated before it is returned. If the
    validatation fails an HTTPBadRequest is raised.
    """
    data, errors = schema.load(obj, many=many)
    if bool(errors):
        err = get_top_error(errors, many)
        raise HTTPBadRequest('Invalid Parameters', err)
    return data


def dump(schema, obj, many=False):
    """Serialize the given object using the schema."""
    return schema.dump(obj, many=many).data
