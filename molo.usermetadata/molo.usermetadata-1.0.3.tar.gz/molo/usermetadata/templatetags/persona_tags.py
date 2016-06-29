from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def persona_selected(context):
    request = context['request']
    if 'MOLO_PERSONA_SELECTED' in request.session:
        selected_persona = request.session['MOLO_PERSONA_SELECTION']
        del request.session['MOLO_PERSONA_SELECTED']
        return selected_persona
    return None
