"""
Project Views
"""

from django.http import JsonResponse
from ..models import Link

# pylint: disable=no-member, unused-argument
def view(request):
    "Example view"
    links = Link.objects.all().values_list('item_one__id',
                                           'item_two__id',
                                           'relation__name')
    return JsonResponse({'response':list(links)})

