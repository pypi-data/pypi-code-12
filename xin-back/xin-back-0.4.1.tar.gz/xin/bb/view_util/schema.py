from marshmallow import validates_schema, ValidationError
from marshmallow_mongoengine import ModelSchema, fields


# TODO: still useful with marshmallow>=2.6 ?
class UnknownCheckedSchema(ModelSchema):

    """
    ModelSchema with check for unknown field
    """

    @validates_schema(pass_original=True)
    def check_unknown_fields(self, data, original_data):
        for key in original_data:
            if key not in self.fields or self.fields[key].dump_only:
                raise ValidationError('Unknown field name {}'.format(key))


class BaseModelSchema(UnknownCheckedSchema):

    """
    Base schema to handle the default fields of a BaseModel
    """
    BASE_FIELDS = ('id', '_version', '_created', '_updated', '_links')
    id = fields.String(dump_only=True)
    _version = fields.Integer(dump_only=True, attribute="doc_version")
    _created = fields.DateTime(dump_only=True, attribute="doc_created")
    _updated = fields.DateTime(dump_only=True, attribute="doc_updated")
    # Shadow the model fields
    doc_version = fields.Skip(load_only=True, dump_only=True)
    doc_created = fields.Skip(load_only=True, dump_only=True)
    doc_updated = fields.Skip(load_only=True, dump_only=True)
    # TODO: move this to marshmallow-mongoengine ?
    _cls = fields.Skip(load_only=True, dump_only=True)
