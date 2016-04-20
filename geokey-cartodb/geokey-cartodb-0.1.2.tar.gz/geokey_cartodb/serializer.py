from json import loads as json_loads

from rest_framework.serializers import BaseSerializer
from rest_framework_gis.serializers import GeoFeatureModelListSerializer


class CartoDbSerializer(BaseSerializer):
    class Meta:
        list_serializer_class = GeoFeatureModelListSerializer

    def convert_value(self, val):
        if val is not None and isinstance(val, str):
            try:  # it's an int
                return int(val)
            except ValueError:
                pass

            try:  # it's a float
                return float(val)
            except ValueError:
                pass

        # cannot convert to number, returns string or None
        return val

    def to_representation(self, obj):
        properties = {}
        for key, value in obj.properties.iteritems():
            properties[key] = self.convert_value(value)

        return {
            'id': obj.id,
            'type': 'Feature',
            'geometry': json_loads(obj.location.geometry.geojson),
            'properties': properties,
            'meta': {
                'status': obj.status,
                'creator': obj.creator.display_name,
                'updator': (obj.updator.display_name
                            if obj.updator is not None else None),
                'created_at': obj.created_at,
                'version': obj.version
            }
        }
