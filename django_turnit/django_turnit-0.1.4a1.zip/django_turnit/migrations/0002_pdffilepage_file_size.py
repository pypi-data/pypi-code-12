# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_turnit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdffilepage',
            name='file_size',
            field=models.PositiveIntegerField(default=0, verbose_name='File size'),
            preserve_default=False,
        ),
    ]
