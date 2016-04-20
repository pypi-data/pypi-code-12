from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from geokey.projects.models import Project
from .models import CartoDbProject
from .serializer import CartoDbSerializer


class IndexPage(LoginRequiredMixin, TemplateView):
    template_name = 'cartodb_index.html'

    def get_context_data(self, *args, **kwargs):
        projects = Project.objects.filter(admins=self.request.user)
        enabled = CartoDbProject.objects.filter(project__in=projects)

        return super(IndexPage, self).get_context_data(
            projects=projects,
            cartodb=enabled,
            protocol=self.request.scheme,
            host=self.request.get_host(),
            *args,
            **kwargs
        )

    def update_projects(self, projects, enabled, form=[]):
        for p in projects:
            if p in enabled and not str(p.id) in form:
                CartoDbProject.objects.get(project=p).delete()
            elif p not in enabled and str(p.id) in form:
                CartoDbProject.objects.create(project=p, enabled=True)

    def post(self, request):
        context = self.get_context_data()
        self.update_projects(
            context.get('projects'),
            [epi.project for epi in context.get('cartodb')],
            self.request.POST.getlist('cartodb_project')
        )
        return self.render_to_response(context)


class ProjectDataView(APIView):
    def get(self, request, project_id):
        try:
            project = CartoDbProject.objects.get(project_id=project_id)

            data = project.project.observations.all()
            serializer = CartoDbSerializer(data, many=True)
            return Response(serializer.data)

        except CartoDbProject.DoesNotExist:
            return Response(
                {'error': 'Project not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
