import datetime
import string
import random

from django.utils import timezone
from django.http import HttpResponse
from django.views.generic import View, TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.gis.geos import GEOSGeometry

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from braces.views import LoginRequiredMixin

from geokey import version
from geokey.core.decorators import handle_exceptions_for_ajax
from geokey.projects.models import Project
from geokey.categories.models import Category
from geokey.contributions.models import MediaFile, Comment
from geokey.contributions.serializers import (
    ContributionSerializer,
    FileSerializer,
    CommentSerializer
)
from geokey.contributions.views.observations import GZipView, GeoJsonView
from geokey.contributions.renderers.geojson import GeoJsonRenderer
from geokey.contributions.renderers.kml import KmlRenderer

from .models import Export


class IndexPage(LoginRequiredMixin, TemplateView):
    template_name = 'export_index.html'

    def get_context_data(self, *args, **kwargs):
        exports = Export.objects.filter(creator=self.request.user)

        return super(IndexPage, self).get_context_data(
            exports=exports,
            *args,
            **kwargs
        )


class ExportExpiryMixin(object):
    def get_expiry(self, expiration_val):
        isoneoff = False
        expiration = None
        if expiration_val == 'one_off':
            isoneoff = True
        elif expiration_val == 'one_week':
            expiration = timezone.now() + datetime.timedelta(days=7)

        return isoneoff, expiration


class ExportCreate(LoginRequiredMixin, ExportExpiryMixin, TemplateView):
    template_name = 'export_create.html'

    def get_context_data(self, *args, **kwargs):
        projects = Project.objects.get_list(self.request.user)

        return super(ExportCreate, self).get_context_data(
            projects=projects,
            *args,
            **kwargs
        )

    def get_hash(self):
        export_check = True

        while export_check:
            urlhash = ''.join([
                random.choice(string.ascii_letters + string.digits)
                for n in xrange(40)
            ])
            export_check = Export.objects.filter(urlhash=urlhash).exists()

        return urlhash

    def post(self, request):
        name = self.request.POST.get('name')

        project_id = self.request.POST.get('project')
        project = Project.objects.get_single(self.request.user, project_id)

        category_id = self.request.POST.get('category')
        category = Category.objects.get_single(
            self.request.user,
            project_id,
            category_id
        )

        isoneoff, expiration = self.get_expiry(
            self.request.POST.get('expiration')
        )

        bounding_box = self.request.POST.get('geometry')
        if bounding_box is not None and len(bounding_box) > 0:
                bounding_box = GEOSGeometry(bounding_box)

        creator = self.request.user
        urlhash = self.get_hash()

        export = Export.objects.create(
            name=name,
            project=project,
            category=category,
            isoneoff=isoneoff,
            expiration=expiration,
            bounding_box=bounding_box,
            urlhash=urlhash,
            creator=creator
        )

        return redirect('geokey_export:export_overview', export_id=export.id)


class ExportGetProjectCategories(LoginRequiredMixin, APIView):

    @handle_exceptions_for_ajax
    def get(self, request, project_id):
        categories = Category.objects.get_list(self.request.user, project_id)
        categories_dict = {}

        for category in categories:
            categories_dict[category.id] = category.name

        return Response(categories_dict, status=status.HTTP_200_OK)


class ExportGetProjectCategoryContributions(GZipView, GeoJsonView):

    @handle_exceptions_for_ajax
    def get(self, request, project_id, category_id):
        categories = Category.objects.get_list(self.request.user, project_id)
        category = categories.get(pk=category_id)
        contributions = category.project.get_all_contributions(
            self.request.user).filter(category=category)

        serializer = ContributionSerializer(
            contributions,
            many=True,
            context={'user': self.request.user, 'project': category.project}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class ExportGetExportContributions(GZipView, GeoJsonView):

    @handle_exceptions_for_ajax
    def get(self, request, export_id):
        try:
            export = Export.objects.get(pk=export_id)

            if export.creator != self.request.user:
                return Response(
                    {'error': 'You must be creator of the export.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            else:
                contributions = export.project.get_all_contributions(
                    self.request.user).filter(category=export.category)

                serializer = ContributionSerializer(
                    contributions,
                    many=True,
                    context={
                        'user': self.request.user,
                        'project': export.project
                    }
                )

                return Response(serializer.data, status=status.HTTP_200_OK)
        except Export.DoesNotExist:
            return Response(
                {'error': 'Export not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class ExportObjectMixin(object):

    def get_context_data(self, export_id, **kwargs):
        try:
            export = Export.objects.get(pk=export_id)

            if export.creator != self.request.user:
                return {
                    'error_description': 'You must be creator of the export.',
                    'error': 'Permission denied.'
                }
            else:
                return super(ExportObjectMixin, self).get_context_data(
                    export=export,
                    **kwargs
                )
        except Export.DoesNotExist:
            return {
                'error_description': 'Export not found.',
                'error': 'Not found.'
            }


class ExportOverview(LoginRequiredMixin, ExportExpiryMixin, ExportObjectMixin,
                     TemplateView):
    template_name = 'export_overview.html'

    def post(self, request, export_id):
        context = self.get_context_data(export_id)

        if context.get('export'):
            export = context['export']

            bounding_box = self.request.POST.get('geometry')
            expiration = self.request.POST.get('expiration')

            if expiration is not None:
                isoneoff, expiration = self.get_expiry(
                    self.request.POST.get('expiration')
                )
                export.isoneoff = isoneoff
                export.expiration = expiration

            if bounding_box is not None and len(bounding_box) > 0:
                export.bounding_box = GEOSGeometry(bounding_box)
            elif bounding_box == '':  # It's in the request but empty
                export.bounding_box = None

            export.save()

        return self.render_to_response(context)


class ExportDelete(LoginRequiredMixin, ExportObjectMixin, TemplateView):
    template_name = 'base.html'

    def get(self, request, export_id):
        context = self.get_context_data(export_id)
        export = context.pop('export', None)

        if export is not None:
            export.delete()

            messages.success(self.request, 'The export has been deleted.')
            return redirect('geokey_export:index')

        return self.render_to_response(context)


class ExportToRenderer(View):

    def get_context(self, request, urlhash):
        context = {
            'PLATFORM_NAME': get_current_site(self.request).name,
            'user': request.user,
            'GEOKEY_VERSION': version.get_version()
        }

        error_context = context.copy()
        error_context.update({
            'error_description': 'The export was not found in the database.',
            'error': 'Not found.'
        })

        try:
            export = Export.objects.get(urlhash=urlhash)
        except Export.DoesNotExist:
            context = error_context
        else:
            if export.is_expired():
                context = error_context
            else:
                context['export'] = export

        return context

    def get(self, request, urlhash, format=None):
        context = self.get_context(request, urlhash)
        export = context.get('export')

        if export and format:
            content_type = 'text/plain'

            if format == 'json':
                renderer = GeoJsonRenderer()
            elif format == 'kml':
                renderer = KmlRenderer()

            contributions = export.project.get_all_contributions(
                export.creator).filter(category=export.category)

            if export.bounding_box is not None:
                contributions = contributions.filter(
                    location__geometry__bboverlaps=export.bounding_box)

            serializer = ContributionSerializer(
                contributions,
                many=True,
                context={'user': export.creator, 'project': export.project}
            )

            protocol = 'https' if request.is_secure() else 'http'
            url = '%s://%s' % (protocol, request.get_host())

            for contribution in serializer.data:
                media = FileSerializer(
                    MediaFile.objects.filter(
                        contribution__id=contribution['id']
                    ),
                    many=True,
                    context={'user': export.creator, 'project': export.project}
                ).data

                for file in media:
                    if not file['url'].startswith('http'):
                        file['url'] = url + file['url']
                    if not file['thumbnail_url'].startswith('http'):
                        file['thumbnail_url'] = url + file['thumbnail_url']

                contribution['media'] = media

                contribution['comments'] = CommentSerializer(
                    Comment.objects.filter(
                        commentto__id=contribution['id'],
                        respondsto=None
                    ),
                    many=True,
                    context={'user': export.creator, 'project': export.project}
                ).data

            content = renderer.render(serializer.data)

            if export.isoneoff:
                export.expire()
        else:
            content = render_to_string('export_access.html', context)
            content_type = 'text/html'

        return HttpResponse(content, content_type=content_type)
