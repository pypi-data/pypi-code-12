# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_turnit.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PDFFilePage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page_file', models.ImageField(upload_to=django_turnit.models.upload_pdf_image_thumbnail, verbose_name='Page de fichier PDF')),
                ('page_id', models.PositiveIntegerField(default=1, verbose_name='Identifiant de la page')),
                ('related_pdf_file', models.CharField(max_length=255, verbose_name='Fichier PDF li\xe9')),
                ('param', models.CharField(max_length=255, null=True, verbose_name='Param\xe8tres de la g\xe9n\xe9ration PDF', blank=True)),
            ],
            options={
                'ordering': ('related_pdf_file', 'page_id'),
                'verbose_name': 'page de document PDF',
                'verbose_name_plural': 'pages de document PDF',
            },
        ),
    ]
