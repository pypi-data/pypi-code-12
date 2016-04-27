import re
from django.http import HttpResponse, Http404

from mauveinternet.markdown import get_models, get_model

# This needs to be added to the URL configuration as /admin/markdown/links
# so that the Javascript can find it.
def links(request):
    """Returns a list of the models and instances of that model
    that can be linked to in the admin models page."""
    if 'model' not in request.GET:
        # output a JSON serialisation of the model list
        return HttpResponse('LinkDialog.updateModels({%s});' % (u',\n'.join([u"'%s': '%s'" % (mname, vname.replace(u"'", u"\\'")) for mname, vname in get_models()])).encode('utf8'), content_type='application/javascript; charset=UTF-8')
    else:
        try:
            model, queryset = get_model(request.GET['model'])
        except ValueError:
            raise Http404()

        links = [(i.pk, unicode(i)) for i in queryset]
        return HttpResponse('LinkDialog.updateInstances({%s})' %
                (u',\n'.join([u"%d: '%s'" % (pk, title.replace("'", "\\'")) for pk, title in links])).encode('utf8'),
                content_type='application/javascript; charset=UTF=8')
