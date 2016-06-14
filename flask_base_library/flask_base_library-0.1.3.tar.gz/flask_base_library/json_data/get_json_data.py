from jsonschema import Draft4Validator, exceptions
from ..DateTimeEncoder.DateTimeEncoder import DateTimeEncoder
import json
import jsonschema


def get_json_data(
        json_string=None,
        json_schema=None
):
    if json_string is None or json_schema is None:
        raise ValueError('JSON string or schema is None (null).')

    _type = json_schema.get('type', None)
    if _type is None or not isinstance(_type, str) or _type.lower() != 'object':
        raise ValueError('Schema type is not correctly defined. Must be an object.')

    _keys = json_schema.get('properties', None)
    if _keys is None:
        raise ValueError('Schema has no properties defined!')

#    if json_string == '':
#        return {}
    try:
        _json_dict = json.loads(json_string, object_hook=DateTimeEncoder.decode)
    except ValueError as ve:
        if json_string in (None, ''):
            exception_string = 'No JSON data was provided'
        else:
            exception_string = 'The JSON data is badly formed, missing, or has syntax errors: {0}'\
                         .format(json_string)
        raise ValueError(exception_string)
    except Exception as e:
        raise jsonschema.ValidationError('Unable to load JSON data: {0}'.format(str(e)))

    valid_schema = False
    try:
        valid_schema = Draft4Validator(json_schema).is_valid(_json_dict)
    except Exception as e:
        pass

    if not valid_schema:
        try:
            json_error_text = ''
            v = Draft4Validator(json_schema)
            loop_counter = 1
            for error in sorted(v.iter_errors(_json_dict), key=str):
                json_error_text += '{0}) {1}; '.format(loop_counter, str(error.message))
                loop_counter += 1
            raise jsonschema.ValidationError(
                'The data passed is invalid and does not match the schema provided. ' +
                'Validation error(s): {0}'.format(json_error_text))
        except Exception as e:
            raise

    return _json_dict
