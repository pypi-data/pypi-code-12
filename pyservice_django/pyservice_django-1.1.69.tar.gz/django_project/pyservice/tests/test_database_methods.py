import pytest

from pyservice.models import ClassA
from pyservice_django.pyservice_django import config_classes


@pytest.mark.django_db(transaction=False)
def test_save():
    config_classes([ClassA])
    a = ClassA()
    result = a.save({'name' : 'TESTE', 'description' : 'AAAAAAAAAAAAAAA'})
    assert result != None


@pytest.mark.django_db(transaction=False)
def test_query():
    config_classes([ClassA])
    a = ClassA()

    query = {'where' : {'id__in' : [1,2]}}

    result = a.query(query)

    assert result != None
