from django_project.pyservice.models import ClassA
from pyservice_django.config import ConfigField


def test_config():
    a = ClassA()

    fields = [ConfigField(klass=ClassA, name='name', label='Name', show=True),
              ConfigField(klass=ClassA, name='description', label='Description', show=True)]

    assert fields[0].type == 'string'
    assert fields[0].maxLength == 10
