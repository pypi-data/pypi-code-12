# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_persona_index(apps, schema_editor):
    from molo.core.models import Main
    from molo.usermetadata.models import PersonaIndexPage
    main = Main.objects.all().first()

    if main:
        persona_index = PersonaIndexPage(title='Personae', slug='Personae')
        main.add_child(instance=persona_index)
        persona_index.save_revision().publish()


class Migration(migrations.Migration):

    dependencies = [
        ('usermetadata', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_persona_index),
    ]
