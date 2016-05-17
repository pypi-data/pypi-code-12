from django.db.models.loading import get_model
from django.forms import ModelForm


#metodo para dejar solo para ver sin editar el campo
class ReadOnlyFieldsMixin(object):
    readonly_fields =()

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFieldsMixin, self).__init__(*args, **kwargs)
        for field in (field for name, field in self.fields.iteritems() if name in self.readonly_fields):
            field.widget.attrs['disabled'] = 'true'
            field.required = False

    def clean(self):
        cleaned_data = super(ReadOnlyFieldsMixin,self).clean()
        for field in self.readonly_fields:
           cleaned_data[field] = getattr(self.instance, field)

        return cleaned_data

def get_form(modelo):
    class MyForm(ModelForm):
        class Meta:
            model = modelo
            exclude = ('id',)
    return MyForm

#actualizar form
def GetForm(request,aplicacion,modelo,obj):
    mymodel = get_model(app_label=aplicacion, model_name=modelo)
    try:
        form=mymodel.FormMetro(request)
    except:
        form=get_form(mymodel)
    return form(instance=obj)

#actualizar form
def GetFormRequest(request,aplicacion,modelo,obj):
    mymodel = get_model(app_label=aplicacion, model_name=modelo)
    try:
        form=mymodel.FormMetro(request)
    except:
        form=get_form(mymodel)
    return form(request.POST,request.FILES,instance=obj)

# #crear form
# def GetCrearForm(request,aplicacion,modelo):
#     mymodel = get_model(app_label=aplicacion, model_name=modelo)
#     try:
#         form=mymodel.FormMetro(request)
#     except:
#         form=get_form(mymodel)
#     return form()
#
# #actualizar form
# def GetCrearFormRequest(request,aplicacion,modelo):
#     mymodel = get_model(app_label=aplicacion, model_name=modelo)
#     form=get_form(mymodel)
#     return form(request.POST)