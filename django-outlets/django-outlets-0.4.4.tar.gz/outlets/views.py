"""Views for the outlets app."""
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404, redirect

from . import models


class OutletsListView(ListView):
    """Lists the outlets of one country."""
    model = models.Outlet

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('slug', '')
        self.all_countries = models.OutletCountry.objects.all()
        if slug:
            self.country = get_object_or_404(models.OutletCountry, slug=slug)
        else:
            try:
                first_country = self.all_countries[0]
            except IndexError:
                raise Http404
            else:
                return redirect(reverse('outlets_list', kwargs={
                    'slug': first_country.slug}))
        return super(OutletsListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(country=self.country)

    def get_context_data(self, **kwargs):
        ctx = super(OutletsListView, self).get_context_data(**kwargs)
        ctx.update({
            'country': self.country,
            'all_countries': self.all_countries,
        })
        return ctx


class MapMarkerInfoboxAJAXView(DetailView):
    """Renders the template for the map marker information bubble."""
    model = models.Outlet
    template_name = 'outlets/outlet_map_marker.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            raise Http404
        return super(MapMarkerInfoboxAJAXView, self).dispatch(
            request, *args, **kwargs)
