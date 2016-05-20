"""
Generate JSON Schema for Marshmallow schemas.

"""
from marshmallow import fields

from microcosm_flask.fields import EnumField
from microcosm_flask.naming import name_for
from microcosm_flask.swagger.naming import type_name


# see: https://github.com/marshmallow-code/apispec/blob/dev/apispec/ext/marshmallow/swagger.py
FIELD_MAPPINGS = {
    fields.Dict: ("object", None),
    fields.Integer: ("integer", "int32"),
    fields.Number: ("number", None),
    fields.Float: ("number", "float"),
    fields.Decimal: ("number", None),
    fields.String: ("string", None),
    fields.Boolean: ("boolean", None),
    fields.UUID: ("string", "uuid"),
    fields.DateTime: ("string", "date-time"),
    fields.Date: ("string", "date"),
    fields.Time: ("string", None),
    fields.Email: ("string", "email"),
    fields.URL: ("string", "url"),
    fields.Field: ("object", None),
    fields.Raw: ("object", None),
    fields.List: ("array", None),
    fields.Nested: (None, None),
    fields.Method: ("object", None),
    EnumField: ("string", None),
}


def build_parameter(field):
    """
    Build a parameter from a marshmallow field.

    See: https://github.com/marshmallow-code/apispec/blob/dev/apispec/ext/marshmallow/swagger.py#L81

    """
    field_type, field_format = FIELD_MAPPINGS[type(field)]
    parameter = {}
    if field_type:
        parameter["type"] = field_type
    if field.metadata.get("description"):
        parameter["description"] = field.metadata["description"]
    if field_format:
        parameter["format"] = field_format
    if field.default:
        parameter["default"] = field.default

    # enums
    enum = getattr(field, "enum", None)
    if enum:
        parameter["enum"] = [choice.name for choice in enum]

    # nested
    if isinstance(field, fields.Nested):
        parameter["$ref"] = "#/definitions/{}".format(type_name(name_for(field.schema)))

    # arrays
    if isinstance(field, fields.List):
        parameter["items"] = build_parameter(field.container)

    return parameter


def build_schema(marshmallow_schema):
    """
    Build JSON schema from a marshmallow schema.

    """
    fields = [
        (name, marshmallow_schema.fields[name])
        for name in sorted(marshmallow_schema.fields.keys())
    ]
    schema = {
        "type": "object",
        "properties": {
            field.dump_to or name: build_parameter(field)
            for name, field in fields
        },
        "required": [
            field.dump_to or name
            for name, field in fields
            if field.required
        ]
    }
    return schema
