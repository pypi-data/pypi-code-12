import pytest

from pyservice.models import ClassA
from pyservice_django.pyservice_django import config_classes


@pytest.mark.django_db(transaction=False)
def test_save():
    config_classes([ClassA])
    a = ClassA()
    result = a.save({'nome' : 'TESTE'})
    assert result != None
