# Copyright (C) 2016 A10 Networks Inc. All rights reserved.

from neutronclient.common import extension
from neutronclient.neutron import v2_0 as neutronV20

_NEUTRON_OPTIONS = ['id', 'tenant_id']

JUST_NONE = object()


class ClientExtension(extension.NeutronClientExtension):

    def _arg_name(self, name, types, prefix="--"):
        if 'a10_type:nullable' in types:
            return self._arg_name(name, types['a10_type:nullable'], prefix)

        if 'a10_type:reference' in types:
            if name.endswith('_id'):
                name = name[:-3]

        """--shish-kabob it"""
        return prefix + name.replace('_', '-')

    def _add_known_arguments(self, parser, required, ignore=[], where=lambda x: True):
        attributes = self.resource_attribute_map[self.resource_plural]
        for name in required:
            parser.add_argument(name)
        for name, attr in attributes.items():
            if name in required or name in _NEUTRON_OPTIONS or name in ignore or not where(attr):
                continue
            types = attr.get('validate', {})
            parser.add_argument(self._arg_name(name, types), dest=name)

            if 'a10_type:nullable' in types:
                parser.add_argument(
                    self._arg_name(name, types, '--no-'),
                    action='store_const',
                    const=JUST_NONE,
                    dest=name)

    def alter_body(self, parsed_args, body):
        return body

    def _transform_arg(self, value, types):
        if value == JUST_NONE:
            return None

        if 'a10_type:nullable' in types:
            return self._transform_arg(value, types['a10_type:nullable'])

        if 'a10_type:reference' in types:
            reference_to = types['a10_type:reference']
            return self.get_resource_id(reference_to, value)

        return value

    def args2body(self, parsed_args):
        attributes = self.resource_attribute_map[self.resource_plural]
        body = {}
        neutronV20.update_dict(parsed_args, body, [a for a in attributes if a != 'id'])

        for k in body:
            types = attributes.get(k, {}).get('validate', {})
            body[k] = self._transform_arg(body[k], types)

        altered = self.alter_body(parsed_args, body)
        return {self.resource: altered}

    def get_resource_id(self, resource, name_or_id):
        client = self.get_client()
        return neutronV20.find_resourceid_by_name_or_id(
            client,
            resource,
            name_or_id)


class List(extension.ClientExtensionList):
    pagination_support = True
    sorting_support = True


class Create(extension.ClientExtensionCreate):

    def _add_known_arguments(self, parser, required, ignore=[]):
        super(Create, self)._add_known_arguments(
            parser,
            required,
            ignore=ignore,
            where=lambda attr: attr.get('allow_post'))

    def add_known_arguments(self, parser):
        return self._add_known_arguments(parser, [])


class Update(extension.ClientExtensionUpdate):

    def _add_known_arguments(self, parser, required, ignore=[]):
        super(Update, self)._add_known_arguments(
            parser,
            required,
            ignore=ignore,
            where=lambda attr: attr.get('allow_put'))

    def add_known_arguments(self, parser):
        return self._add_known_arguments(parser, [])


class Delete(extension.ClientExtensionDelete):
    pass


class Show(extension.ClientExtensionShow):
    pass
