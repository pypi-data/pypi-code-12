# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('file', models.FileField(max_length=255, upload_to=b'uploads/%Y/%m/%d/files/')),
            ],
        ),
        migrations.CreateModel(
            name='ImageUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('image', models.ImageField(max_length=255, upload_to=b'uploads/%Y/%m/%d/images/')),
            ],
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(max_length=255, upload_to=b'uploads/%Y/%m/%d/images/')),
            ],
        ),
        migrations.CreateModel(
            name='ThumbnailSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('height', models.PositiveIntegerField()),
                ('width', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('width', 'height'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='thumbnailsize',
            unique_together=set([('height', 'width')]),
        ),
        migrations.AddField(
            model_name='thumbnail',
            name='size',
            field=models.ForeignKey(to='uploader.ThumbnailSize'),
        ),
        migrations.AddField(
            model_name='thumbnail',
            name='upload',
            field=models.ForeignKey(to='uploader.ImageUpload'),
        ),
        migrations.AddField(
            model_name='imageupload',
            name='resize_image',
            field=models.ManyToManyField(help_text=b'Choose the size or sizes you would like the system to create for you. Choose none of the sizes to preserve the dimensions of the image you are uploading.', to='uploader.ThumbnailSize', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='thumbnail',
            unique_together=set([('upload', 'size')]),
        ),
    ]
