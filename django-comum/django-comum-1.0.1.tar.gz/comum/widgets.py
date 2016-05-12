# coding: utf-8
from django.contrib.gis.geos import *
from django.forms import widgets


class CoordenadaWidget(MultiWidget):
    """
    Classe que representa um widget simples para
    input de uma coordenada
    """

    _widgets = None
    _x_widget = None
    _y_widget = None
    _z_widget = None

    def __init__(self, has_z=False, attrs=None):

        _x_widget = widgets.TextInput(attrs=attrs)
        _y_widget = widgets.TextInput(attrs=attrs)

        _widgets = [_x_widget, _y_widget]

        if has_z:
            _z_widget = widgets.TextInput(attrs=attrs)
            _widgets.append(_z_widget)

        super(CoordenadaWidget, self).__init__(*args, **kwargs)

    def decompress(self, value):
        """
        descomprime o valor de um ponto ou uma tupla
        para o widget
        """

        if value:

            if isinstance(value, Point):
                valor = [value.x, value.y]

                if value.hasz:
                    valor.append(value.z)

                return valor

            if isinstance(value, tuple):
                valor = [value[0], value[1]]

                if len(value) > 2:
                    valor.append(value[2])

                return valor
        else:

            if self.has_z:
                return [None, None, None]

            else:
                return [None, None]
