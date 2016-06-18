from django_lare.models import Lare


class LareMiddleware(object):
    def process_request(self, request):
        request.lare = Lare(request)

    def process_response(self, request, response):
        if request.lare.is_enabled():
            response['X-LARE-VERSION'] = request.lare.version
        return response
