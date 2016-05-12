# coding: utf-8
from django.utils.translation import ugettext as _


TIPO_LINHA_COMERCIAL = "C"
TIPO_LINHA_RESIDENCIAL = "R"
TIPO_LINHA_AUTOMATICA = "A"

TIPO_LINHA_CHOICES = ((TIPO_LINHA_COMERCIAL, _(u"Comercial")),
                      (TIPO_LINHA_RESIDENCIAL, _(u"Residencial")),
                      (TIPO_LINHA_AUTOMATICA, _(u"Automática")))

SEXO_M = "M"
SEXO_F = "F"
SEXO_N = "N"

SEXO_CHOICES = ((SEXO_M, _(u"Masculino")),
                (SEXO_F, _(u"Feminino")),
                (SEXO_N, _(u"Não declarado")))
