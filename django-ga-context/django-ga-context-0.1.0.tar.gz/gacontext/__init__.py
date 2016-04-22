from django.conf import settings


def ga_processor(request):
    return {
        'GA_CODE': getattr(settings, 'GA_CODE', None),
    }
