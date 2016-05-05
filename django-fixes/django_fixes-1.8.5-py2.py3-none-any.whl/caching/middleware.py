
class NoCacheMiddleware(object):
    """Sets headers to stop caching. Improved in django-1.9 (@django.views.decorators.cache.never_cache decorator) but may still not have a complete solution (esp as middleware)."""
    def process_response(self,request,response):
        response['Cache-Control']='max-age=0, no-cache, no-store, must-revalidate, proxy-revalidate'
        response['Pragma']='no-cache'
        response['Expires']='0'
        return response
