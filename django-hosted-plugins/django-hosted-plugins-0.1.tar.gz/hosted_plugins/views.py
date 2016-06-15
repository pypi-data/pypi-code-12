import os
from django.utils.decorators import classonlymethod
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.shortcuts import redirect
from django.http.response import HttpResponse, Http404
from rest_framework import viewsets
from hosted_plugins import serializers
from hosted_plugins import permissions

class UpdateViewSet(viewsets.ReadOnlyModelViewSet):
    model = serializers.models.Update
    serializer_class = serializers.UpdateSerializer
    permission_classes = [permissions.ReadOnly,]
    lookup_value_regex = '[^/.]+)/(?P<plugin>[\w-]+)-(?P<version>[\d.]+).(?P<download>zip|tar.gz'
    
    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        return never_cache(super(cls, UpdateViewSet).as_view(actions=actions, **initkwargs))
    
    def is_detail_request(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        return lookup_url_kwarg in self.kwargs
    
    def get_queryset(self):
        queryset = self.model.objects.filter(platform__platform__iexact=self.kwargs['platform'])
        if not self.is_detail_request():
            queryset = queryset.select_related('platform').order_by('-release_date')[:1]
        return queryset
    
    def head(self, request, *args, **kwargs):
        obj = self.get_object() if self.is_detail_request() else self.filter_queryset(self.get_queryset())[0]
        response = HttpResponse(content_type=obj.mime_type)
        x_header = 'X-%(plugin)s-For-%(platform)s-' % {
            'plugin': obj.platform.plugin,
            'platform': obj.platform.platform
        }
        response[x_header + 'Version'] = obj.version
        response[x_header + 'Location'] = obj.url
        return response
    
    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.downloads += 1
        obj.save(update_fields=['downloads'])
        file_name = obj.filename
        file_path = os.path.join(settings.MEDIA_ROOT, 'plugins', obj.platform.platform.lower(), file_name)
        try:
            file_data = open(file_path, 'rb').read()
        except EnvironmentError:
            raise Http404(file_name + ' does not exist or access denied')
        response = HttpResponse(file_data, content_type=obj.mime_type)
        response['Content-Disposition'] = 'attachment; filename="%(filename)s"' % {'filename': file_name}
        return response
