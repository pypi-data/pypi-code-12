# -*- coding: utf-8 -*-
import os
import json
from django.views.generic.edit import BaseFormView
from django.http import HttpResponse
from vectortools.geojson import convert_to_merged_geojson_data
from vectortools.fsutils import TempDir
from vectortools.reader import VectorReaderError
from .forms import FileUploadForm

class AnyVectorFormatToGeojsonView(BaseFormView):
    http_method_names = ['post',]
    response_class = HttpResponse
    form_class = FileUploadForm
    
    def render_to_response(self, context, **response_kwargs):
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            json.dumps(context),
            **response_kwargs
        )
    
    def success(self, data):
        return self.render_to_response({'success': True, 'result': data})
    
    def fail(self, error=None):
        return self.render_to_response({'success': False, 'error': error})
    
    def form_valid(self, form):
        uploaded_file = form.cleaned_data['file']
        tmp_dir = TempDir()
        dst_file = open(os.path.join(tmp_dir.path, uploaded_file.name), 'w')
        for c in uploaded_file.chunks():
            dst_file.write(c)
        dst_file.close()
        try:
            geojson_data = convert_to_merged_geojson_data(dst_file.name)
        except VectorReaderError:
            return self.fail(u'не удалось открыть файл')
        return self.success(geojson_data)
        
    def form_invalid(self, form):
        return self.fail(form.errors)
