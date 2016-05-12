# coding: utf-8
from django import forms
from django.utils.translation import ugettext as _
from .models import DominioMixIn, DominioPonderadoMixIn, Anexo, Fotografia


class AnexoForm(forms.ModelForm):
    """
    Formulário para anexação de arquivo
    """

    class Meta:
        model = Anexo
        fields = '__all__'


class FotografiaForm(forms.ModelForm):

    class Meta:
        model = Fotografia
        fields = '__all__'


class DominioForm(forms.Form):
    codigo = forms.CharField(max_length=12,
                             label=_(u"Código"),
                             help_text=_(u"Código do domínio. Este valor será armazenado no banco de dados."))

    valor = forms.CharField(max_length=64,
                            label=_(u"Valor"),
                            help_text=_(u"Valor que será utilizado para mostrar para o usuário nas telas do sistema."))


class DominioPonderadoForm(DominioForm):

    peso = forms.IntegerField(min_value=0,
                              label=_(u"Peso"),
                              help_text=_(u"Peso para este valor. O peso é utilizado por rotinas internas do sistema para cálculos diversos."))
