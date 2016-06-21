# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import warnings
import sys

from django.core.management.color import no_style
from django.db import migrations


def create_static_page_category(apps, schema_editor):
    Category = apps.get_model('cfblog', 'Category')
    sys.stdout.write('Creating the static pages category')
    if Category.objects.filter(id=1):
        warnings.warn(
            "Entry for static pages already exists."
        )
    else:
        reset_sequence = True
        if Category.objects.count():
            reset_sequence = False

        Category.objects.create(
            id=1,
            title='Static Page',
            description='All the standalone pages should be under this category'
        )

        if reset_sequence:
            connection = schema_editor.connection
            sql_statements = connection.ops.sequence_reset_sql(no_style(), [Category])
            operation = migrations.RunSQL(sql=sql_statements)
            operation.database_forwards('cfblog', schema_editor, None, None)


def delete_static_page_category(apps, schema_editor):
    Category = apps.get_model('cfblog', 'Category')
    categories = Category.objects.filter(id=1)
    sys.stdout.write('Deleting the static pages category')
    if categories:
        categories.delete()
    else:
        warnings.warn(
            "Entry for static pages does not exist."
        )


class Migration(migrations.Migration):

    dependencies = [
        ('cfblog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            code=create_static_page_category,
            reverse_code=delete_static_page_category
        )
    ]
