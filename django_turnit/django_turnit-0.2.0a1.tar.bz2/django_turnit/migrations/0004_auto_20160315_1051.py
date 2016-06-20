# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_turnit', '0003_auto_20160315_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdffilepage',
            name='file_size',
            field=models.PositiveIntegerField(null=True, verbose_name='File size', blank=True),
        ),
    ]
