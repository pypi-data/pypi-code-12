#encoding:utf-8
from django.test import TestCase
from .modulos.saldos_clientes.core import formar_mensaje
from django_microsip_base.libs.models_base.models import Registry
modo_pruebas = True


class FormarMensajeTests(TestCase):
    def setUp(self):
        cliente_id = 3636
        cliente = {
            'total': 23900,
            'numero_documentos': 3,
            'email': 'jesusmaherrera@gmail.com',
            'telefono': '6251208151',
            'moneda_nombre': 'Moeda Nacional',
            'moneda_simbolo': 'MN',
            'documentos': [],
        }

        cliente_cargos = {
            'email': cliente['email'],
            'telefono': cliente['telefono'],
            'documentos_numero': cliente['numero_documentos'],
            'documentos': cliente['documentos'],
            'total': '$ {:,.2f}'.format(cliente['total']),
            'cliente_moneda': cliente['moneda_nombre'],
            'cliente_moneda_simbolo': cliente['moneda_simbolo'],
            'cliente_id': cliente_id,
        }

        login = {
            'apikey': Registry.objects.get(nombre='SIC_SMS_ApiKey').valor,
        }

        commun = {
            'empresa_nombre': Registry.objects.get(nombre='SIC_SMS_NombreEmpresa').get_value(),
        }

        self.cliente_cargos_kwargs = {
            'commun': commun,
            'login': login,
            'cargo': cliente_cargos,
        }

    def test_donot_send_in_messaje_morethan_60chars(self):
        """ Para probar que en la variable de mensaje no se envien mas de 60 caracteres."""
        mensaje = formar_mensaje(kwargs=self.cliente_cargos_kwargs)
        mensaje_len = len(mensaje)
        print mensaje_len
        self.assertTrue(mensaje_len < 60)
