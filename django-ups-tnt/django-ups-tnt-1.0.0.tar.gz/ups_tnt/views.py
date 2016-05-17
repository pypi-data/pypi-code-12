from django.core.cache import caches
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TimeInTransitRequestSerializer
from .tnt import fetch_estimated_arrival_times
from . import settings


cache = caches[settings.UPS_CACHE_NAME]


class TimeInTransitView(APIView):
    """ Uses UPS Time In Transit API to estimate delivery date
    `postal_code` is required for a location.
    `country_code`, `city`, `state_province_code` are optional

    Example json request

    ```
    {
        "ship_to": {
            "city": "New York",
            "state_province_code": "NY",
            "postal_code": "10031"
        }
    }
    ```
    """

    def _build_cache_key(self, data):
        key = 'ups_tnt_1_%s_%s_%s' % (
            data.get('ship_from'),
            data.get('ship_to'),
            data.get('pickup_date')
        )
        # Remove memcached unfriendly chars
        return key.translate({ord(i): None for i in '[]:() '})

    def post(self, request, format=None):
        serializer = TimeInTransitRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cache_key = self._build_cache_key(serializer.validated_data)
        response_data = cache.get(cache_key)
        if response_data is None:
            response_data = fetch_estimated_arrival_times(
                **serializer.validated_data)
            cache.set(cache_key, response_data, 60 * 60)  # Cache for 1 hour

        return Response(response_data)
