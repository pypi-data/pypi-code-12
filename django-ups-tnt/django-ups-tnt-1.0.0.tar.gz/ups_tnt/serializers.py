from rest_framework import serializers


class LocationSerializer(serializers.Serializer):
    city = serializers.CharField(
        max_length=30, required=False, allow_blank=True, allow_null=True)
    state_province_code = serializers.CharField(
        max_length=30, required=False, allow_blank=True, allow_null=True)
    country_code = serializers.CharField(
        max_length=2, allow_blank=True, default="US")
    postal_code = serializers.CharField(max_length=10)


class TimeInTransitRequestSerializer(serializers.Serializer):
    ship_from = LocationSerializer(default=[])
    ship_to = LocationSerializer(default=[])
    pickup_date = serializers.DateField(default=None, allow_null=True)
