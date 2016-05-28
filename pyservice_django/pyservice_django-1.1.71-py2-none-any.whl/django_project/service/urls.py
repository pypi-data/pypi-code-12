"""service_example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from pyservice.models import ClassA
from pyservice_django import pyservice_django


def view(request):
    pyservice_django.service_name = 'Servico Usuario, responsavel por processar toda e qualquer requisicao, determinar permissoes, orquestrar execucoes'
    pyservice_django.service_description = ''
    pyservice_django.service_version = '2.0'
    pyservice_django.config_classes([ClassA])
    pyservice_django.add_route('/save', ClassA().save)
    pyservice_django.add_route('/delete', ClassA().delete)
    pyservice_django.add_route('/create', ClassA().create)
    pyservice_django.add_route('/list', ClassA().query)
    return pyservice_django.processa_django_request(request)


urlpatterns = [
    url(r'^.*', view)
]
