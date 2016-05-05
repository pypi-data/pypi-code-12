# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0028_merge'),
        ('usermetadata', '0002_create_index_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonaeSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('persona_required', models.BooleanField(default=False, verbose_name='Activate Personae')),
                ('site', models.OneToOneField(editable=False, to='wagtailcore.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='personapage',
            options={'verbose_name': 'Persona', 'verbose_name_plural': 'Personae'},
        ),
    ]
