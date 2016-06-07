import logging

import jsonschema
from jsonschema.exceptions import ValidationError

logger = logging.getLogger("validator")


class ValidatorMixin(object):
    _schema = {
        "type": "object",
        "properties": {}
    }

    @classmethod
    def check_schema(cls):
        jsonschema.Draft4Validator.check_schema(cls._schema)

    @classmethod
    def validate(cls, data, silent=True):
        try:
            jsonschema.validate(data, cls._schema)
            return True
        except ValidationError as e:
            if not silent:
                logger.warn(e)
            return False
