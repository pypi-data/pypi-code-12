"""
Project Views
"""

from django.http import JsonResponse
from .tools import by_request

def view(request):
    "Example view"
    return JsonResponse(by_request.guess_country_language_currency(request))

