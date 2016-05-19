# coding=utf-8

from django.shortcuts import HttpResponse, get_object_or_404

from . import models as _models


def leonid_file_view(request, name):
    seo_file = get_object_or_404(_models.LeonidFile, name=name)
    content = seo_file.content
    content_type = seo_file.content_type
    return HttpResponse(content=content, content_type=content_type)
