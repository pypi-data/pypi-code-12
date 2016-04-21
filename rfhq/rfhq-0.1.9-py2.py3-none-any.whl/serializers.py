# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

from rest_framework.settings import api_settings
from rest_framework.utils import html
from rest_framework.exceptions import ValidationError


class ActionExcludesModelFieldsMixin(object):

    def get_field_names(self, declared_fields, info):
        fields = list(super(ActionExcludesModelFieldsMixin, self).get_field_names(declared_fields, info))
        action_excludes = getattr(self.Meta, 'action_excludes', {}).get(getattr(self.context.get('view'), 'action', None), [])
        return [field for field in fields if field not in action_excludes]


class LenientBulkCreateSerializerMixin(object):

    def to_internal_value(self, data):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if html.is_html_input(data):
            data = html.parse_html_list(data)

        if not isinstance(data, list):
            message = self.error_messages['not_a_list'].format(input_type=type(data).__name__)
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [message]})

        ret = []
        errors = []

        for item in data:
            try:
                validated = self.child.run_validation(item)
            except ValidationError as exc:
                errors.append({"errors": exc.detail, "item": item})
            else:
                ret.append(validated)

        self.bulk_validation_errors = errors
        return ret
