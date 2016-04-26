# -*- coding: utf-8 -*-
'''
Validates cadaster parcel in Flanders
'''

import colander
from crabpy.gateway.exception import GatewayRuntimeException, GatewayResourceNotFoundException
from colander import null


class CadasterSchemaNode(colander.MappingSchema):

    afdeling = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50),
        missing=None
    )

    sectie = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50),
        missing=None
    )

    perceel = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50),
        missing=None
    )

    capakey = colander.SchemaNode(
        colander.String(50),
        validator=colander.Length(1, 50)
    )

    def preparer(self, parcel):
        if parcel is None or not parcel:
            return null  # pragma: no cover
        return parcel

    def validator(self, node, parcel):
        request = self.bindings['request']
        capakey_gateway = request.capakey_gateway()
        try:
            parcel_data = capakey_gateway.get_perceel_by_capakey(parcel['capakey'])
            parcel['afdeling'] = parcel_data.sectie.afdeling.naam
            parcel['sectie'] = parcel_data.sectie.id
            parcel['perceel'] = parcel_data.id
        except (GatewayRuntimeException, AttributeError, GatewayResourceNotFoundException):
            raise colander.Invalid(
                    node,
                    'Ongeldige capakey'
            )

