# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, division, print_function, unicode_literals
from django.db import models, migrations
import emails.models
import django.utils.timezone
import fluo.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('filename', models.CharField(null=True, default=None, verbose_name='filename', blank=True, max_length=255)),
                ('content', models.BinaryField(null=True, default=None, verbose_name='content', blank=True)),
                ('mimetype', models.CharField(null=True, default=None, verbose_name='mimetype', blank=True, max_length=255)),
            ],
            options={
                'verbose_name_plural': 'attachments',
                'verbose_name': 'attachment',
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', fluo.db.models.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('last_modified_at', fluo.db.models.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('from_email', models.CharField(default=emails.models._get_default_from_email, verbose_name='from email', max_length=255)),
                ('to_emails', models.CharField(default='', verbose_name='to emails', blank=True, max_length=255)),
                ('cc_emails', models.CharField(default='', verbose_name='cc emails', blank=True, max_length=255)),
                ('bcc_emails', models.CharField(default='', verbose_name='bcc emails', blank=True, max_length=255)),
                ('all_recipients', models.TextField(default='', verbose_name='recipients', blank=True)),
                ('headers', models.TextField(default='', verbose_name='headers', blank=True)),
                ('subject', models.CharField(verbose_name='subject', max_length=255)),
                ('body', models.TextField(verbose_name='body')),
                ('raw', models.TextField(default='', verbose_name='raw message', blank=True)),
            ],
            options={
                'verbose_name_plural': 'emails',
                'verbose_name': 'email',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', fluo.db.models.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('last_modified_at', fluo.db.models.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('from_email', models.CharField(default=emails.models._get_default_from_email, verbose_name='from email', max_length=255)),
                ('default_to', models.CharField(null=True, verbose_name='default to', help_text='comma separated value', max_length=255, blank=True)),
                ('default_cc', models.CharField(null=True, verbose_name='default cc', help_text='comma separated value', max_length=255, blank=True)),
                ('default_bcc', models.CharField(null=True, verbose_name='default bcc', help_text='comma separated value', max_length=255, blank=True)),
                ('name', models.CharField(db_index=True, unique=True, verbose_name='name', max_length=255)),
                ('subject', models.CharField(verbose_name='subject', max_length=255)),
                ('body', models.TextField(verbose_name='body')),
                ('body_html', models.TextField(default='', verbose_name='html body', blank=True)),
                ('noreply', models.BooleanField(default=False, verbose_name='no reply', help_text='should add a Reply-to with noreply@domain header')),
            ],
            options={
                'verbose_name_plural': 'email templates',
                'verbose_name': 'email template',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EmailTemplateTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('language', models.CharField(db_index=True, verbose_name='language', choices=[('en', 'English'), ('de', 'German'), ('fr', 'French'), ('es', 'Spanish'), ('it', 'Italian')], max_length=5)),
                ('subject', models.CharField(verbose_name='subject', max_length=255)),
                ('body', models.TextField(verbose_name='body')),
                ('body_html', models.TextField(default='', verbose_name='body', blank=True)),
                ('parent', models.ForeignKey(related_name='translations', to='emails.EmailTemplate', verbose_name='parent')),
            ],
            options={
                'verbose_name_plural': 'mail translations',
                'verbose_name': 'mail translation',
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='email',
            field=models.ForeignKey(related_name='attachments', to='emails.Email', verbose_name='email'),
        ),
        migrations.AlterUniqueTogether(
            name='emailtemplatetranslation',
            unique_together=set([('language', 'parent')]),
        ),
    ]
