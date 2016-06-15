from __future__ import unicode_literals

import aboutconfig.utils
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='Period separated strings. All keys are case-insensitive.', max_length=512, unique=True, validators=[django.core.validators.RegexValidator('^(\\w+\\.)*\\w+$')])),
                ('value', models.CharField(blank=True, max_length=1024, null=True)),
                ('default_value', models.CharField(editable=False, help_text='Default value set by setting provider. Used by 3rd-party apps.', max_length=1024)),
                ('allow_template_use', models.BooleanField(default=True, help_text='Prevent settings from being accessible via the template filter. Can be useful for API-keys, for example')),
            ],
        ),
        migrations.CreateModel(
            name='DataType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('serializer_class', models.CharField(help_text='Must be a class that implements serialize, unserialize and validate methods.', max_length=256, validators=[aboutconfig.utils.serializer_validator])),
            ],
        ),
        migrations.AddField(
            model_name='config',
            name='data_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='aboutconfig.DataType'),
        ),
    ]
