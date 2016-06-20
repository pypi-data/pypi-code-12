# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_turnit', '0004_auto_20160315_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdffilepage',
            name='pdffile_hash',
            field=models.CharField(max_length=512, null=True, verbose_name='Hash of the PDF file', blank=True),
        ),
    ]
