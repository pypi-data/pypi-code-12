# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.views.generic.detail import DetailView
from .models import Timeline


class TimelineDetailView(DetailView):
    template = "timelines/timeline.html"

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        return self.object.to_dict()

    def get_queryset(self):
        self.preview = self.kwargs.get('preview', False)
        if self.preview:
            return Timeline.objects.all()
        else:
            return Timeline.objects.filter(published=True)

    def render_to_response(self, context):
        my_context = {
            'preview': self.preview
        }
        my_context.update(context)

        # Look for a 'format=json' GET argument
        if self.kwargs.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super(TimelineDetailView, self).render_to_response(my_context)
