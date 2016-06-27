# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ('wagtailcore', '0001_initial'),        
    ]

    operations = [
        migrations.RunSQL('DROP INDEX IF EXISTS page_fts_idx'),
        migrations.RunSQL("CREATE INDEX page_fts_idx ON wagtailcore_page USING gin(to_tsvector('english', title));")
    ]
