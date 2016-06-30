# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_turnit', '0002_pdffilepage_file_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='pdffilepage',
            name='related_pdf_field',
            field=models.CharField(default='', max_length=255, verbose_name='Related PDF file field'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pdffilepage',
            name='related_pdf_file',
            field=models.CharField(max_length=512, verbose_name='Related PDF file path'),
        ),
    ]
