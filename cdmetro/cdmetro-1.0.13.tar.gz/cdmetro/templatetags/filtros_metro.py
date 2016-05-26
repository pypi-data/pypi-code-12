from django import template
from django.db.models.loading import get_models, get_model
import humanize

register = template.Library()

@register.simple_tag
def valor_field(id,valor,aplicacion,modelo):
    mymodel = get_model(app_label=aplicacion, model_name=modelo)
    val_aux=mymodel.objects.filter(id=id).values_list(valor,flat=True)
    # if '__' in valor:
    #     val = valor.split('__')
    #     #print val[0]
    #     print val_aux.model._meta.get_field(val[0]).get_internal_type()
    # else:
    #     print val_aux.model._meta.get_field(valor).get_internal_type()
    if str(val_aux[0]) == 'False':
        return '<a class="btn btn-primary red" ><i class="halflings-icon white remove-sign"></i></a>'
    elif str(val_aux[0]) == 'True':
        return '<a class="btn green" ><i class="halflings-icon white ok-sign"></i></a>'
    else:
        return val_aux[0]

@register.filter(name='access')
def access(value, arg):
    return value[arg]

@register.filter(name='filtros')
def filtros(value,arg):
	if arg == 'intcomma':
		value = humanize.intcomma(value)
	return value
