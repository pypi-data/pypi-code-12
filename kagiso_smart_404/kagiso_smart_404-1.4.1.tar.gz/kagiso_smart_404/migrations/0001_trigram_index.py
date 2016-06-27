# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ('wagtailcore', '0001_initial'),        
    ]

    operations = [
        migrations.RunSQL('CREATE EXTENSION IF NOT EXISTS pg_trgm'),
        migrations.RunSQL('DROP INDEX IF EXISTS slug_trgm_idx'),
        migrations.RunSQL('CREATE INDEX slug_trgm_idx ON wagtailcore_page USING gin (slug gin_trgm_ops)')
    ]
