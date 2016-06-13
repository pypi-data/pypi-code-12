from __future__ import unicode_literals

from django.db import migrations

from ..serializers import BoolSerializer, IntSerializer, StrSerializer, DecimalSerializer

def get_path(klass):
    return '{}.{}'.format(klass.__module__, klass.__name__)


def load_data_types(apps, schema_editor):
    DataType = apps.get_model('aboutconfig', 'DataType')

    DataType.objects.create(name='Boolean', serializer_class=get_path(BoolSerializer))
    DataType.objects.create(name='Integer', serializer_class=get_path(IntSerializer))
    DataType.objects.create(name='String', serializer_class=get_path(StrSerializer))
    DataType.objects.create(name='Decimal', serializer_class=get_path(DecimalSerializer))


class Migration(migrations.Migration):

    dependencies = [
        ('aboutconfig', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data_types)
    ]
