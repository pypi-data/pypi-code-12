from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import get_language_from_request
from molo.core.utils import get_locale_code
from molo.usermetadata.models import PersonaPage


class PersonaView(TemplateView):
    template_name = 'persona.html'

    def get_context_data(self, *args, **kwargs):
        persona_pages = PersonaPage.objects.live().filter(
            languages__language__is_main_language=True)
        context = super(PersonaView, self).get_context_data(*args, **kwargs)
        locale_code = get_locale_code(get_language_from_request(self.request))
        context.update({
            'persona_pages':
            [a.get_translation_for(locale_code) or a for a in persona_pages],
            'next': self.request.GET.get('next', '/')})
        return context


def set_persona(request, persona_id):
    persona = get_object_or_404(PersonaPage, pk=persona_id)
    request.session['MOLO_PERSONA_SELECTION'] = persona.slug
    request.session['MOLO_PERSONA_SELECTED'] = True
    return HttpResponseRedirect(request.GET.get('next', '/'))


def skip_persona(request):
    request.session['MOLO_PERSONA_SELECTION'] = 'skip'
    return HttpResponseRedirect(request.GET.get('next', '/'))
