import json
import os
import zipfile

import django
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import ListView

try:
    from sorl.thumbnail import get_thumbnail
except ImportError:
    from easy_thumbnails.files import get_thumbnailer

from .models import ImageUpload, FileUpload, ThumbnailSize


class LinkListView(ListView):
    use_old_output_style = False

    def get_queryset(self):
        return FileUpload.objects.all().order_by("-id")

    def get(self, request, *args, **kwargs):
        self.links = []

        for f in self.get_queryset():
            self.links.append({
                'title': f.name,
                'value': f.file.url,
            })

        if 'django.contrib.flatpages' in settings.INSTALLED_APPS:
            from django.contrib.flatpages.models import FlatPage

            for fp in FlatPage.objects.all():
                self.links.append({
                    'title': fp.title,
                    'value': fp.url,
                })

        if not self.use_old_output_style:
            return HttpResponse(
                json.dumps(self.links),
                content_type='application/json',
            )
        else:
            return super(LinkListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            'links': self.links,
        }


class ImageListView(ListView):
    use_old_output_style = False

    def get_queryset(self):
        return ImageUpload.objects.all().order_by("-id")

    def get(self, request, *args, **kwargs):
        if not self.use_old_output_style:
            images = []

            if not getattr(settings, 'NO_IMAGE_LIST', False):
                for image in self.get_queryset():
                    images.append({
                        'title': image.name,
                        'value': image.image.url,
                    })

                    for tn in image.thumbnail_set.all():
                        images.append({
                            'title': str(tn),
                            'value': tn.image.url,
                        })

            return HttpResponse(
                json.dumps(images),
                content_type='application/json',
            )
        else:
            return super(ImageListView, self).get(request, *args, **kwargs)


@user_passes_test(lambda u: u.is_staff)
def all_files(request, template_name="uploader/all_files.html"):

    class FilesUploadForm(forms.Form):
        file = forms.FileField(label="File or Zip Archive Upload")

    class SearchForm(forms.Form):
        keywords = forms.CharField(label="Keywords", required=False)

    def add_file(filename, content, overwrite=False):
        ext = filename.rsplit(".", 1)[1].lower()
        filename = os.path.basename(filename).rsplit(".")[0]
        filename = "%s (%s)" % (filename.replace("_", ' '), ext.upper())

        try:

            if ext in ("gif", "svg", "jpg", "bmp", "jpeg", "png"):
                upload = ImageUpload(name=filename, image=content)
            else:
                upload = FileUpload(name=filename, file=content)
            upload.save()
#            if ext in ("gif", "svg", "jpg", "bmp", "jpeg", "png"):
#                upload,created = ImageUpload.objects.get_or_create(name=filename, defaults={"image": content})
#            else:
#                upload,created = FileUpload.objects.get_or_create(name=filename, defaults={"file": content})
            return upload
        except Exception, ex:
            print ex

    keywords = ""
    if request.method == "POST":
        type = request.POST.get("type")

        if "file" in request.FILES:
            form = FilesUploadForm(request.POST, request.FILES)
            if form.is_valid():
                data_file = form.cleaned_data["file"]
                first_file = None
                try:
                    if data_file.name.endswith(".zip"):
                        file_handle = data_file.open("r")
                        zip = zipfile.ZipFile(data_file)
                        for filename in zip.namelist():
                            if filename.find(".") > -1:
                                file = SimpleUploadedFile(name=filename, content=zip.read(filename))
                                upload = add_file(filename, file)
                    else:
                        raise zipfile.BadZipfile("Not a zip file")
                except zipfile.BadZipfile:
                    upload = add_file(data_file.name, data_file)
                    if upload:
                        first_file = upload
                print "First: %s, Upload: %s" % (first_file, upload)
        else:
            form = FilesUploadForm()

        search_form = SearchForm()
    else:
        type = request.GET.get("type")
        form = FilesUploadForm()

        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            keywords = search_form.cleaned_data['keywords']

    try:
        ipage = int(request.GET.get('ipage', '1'))
    except ValueError:
        raise Http404

    try:
        fpage = int(request.GET.get('fpage', '1'))
    except ValueError:
        raise Http404

    if not type or type == "image":
        images = ImageUpload.objects.exclude(image="").order_by("-id")
        if keywords:
            images = images.filter(
                *[Q(name__icontains=kw) | Q(image__icontains=kw) for kw in keywords.split()]
            )
        image_paginator = Paginator(images, 21)
        image_page = image_paginator.page(ipage)
        sizes = ThumbnailSize.objects.all()

    if not type or type in ('file', 'media'):
        files = FileUpload.objects.all().order_by("-id")
        if keywords:
            files = files.filter(*[Q(name__icontains=kw) | Q(file__icontains=kw) for kw in keywords.split()])
        file_paginator = Paginator(files, 14)
        file_page = file_paginator.page(fpage)

    django_version = django.VERSION

    if (
        django_version[0] == 1 and
        django_version[1] == 8
    ):
        jquery_path = 'admin/js/jquery.js'
    else:
        jquery_path = 'admin/js/vendor/jquery/jquery.js'

    return render_to_response(
        template_name,
        locals(),
        context_instance=RequestContext(request)
    )


@user_passes_test(lambda u: u.is_staff)
def create_thumbnail(request, id, width=0, height=0):
    try:
        image = ImageUpload.objects.get(id=id)
    except ImageUpload.DoesNotExist:
        raise Http404
    if int(width) > 0 and int(height) > 0:
        try:
            thumbnail = get_thumbnail(
                image.image.name,
                '%sx%s' % (width, height),
            )
        except NameError:
            thumbnail = get_thumbnailer(image.image).get_thumbnail({
                'size': (width, height),
            })

        return HttpResponse("%s" % thumbnail.url)
    else:
        return HttpResponse("%s" % image.image.url)
