# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import enumerify.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mandrill_logger', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='reason',
            field=enumerify.fields.SelectIntegerField(default=0, db_index=True, choices=[(0, b'Not Available'), (1, b'Hard Bounce'), (2, b'Soft Bounce'), (3, b'Spam'), (4, b'Unsub'), (5, b'Custom'), (6, b'Invalid Sender'), (7, b'Invalid'), (8, b'Test Mode Limit'), (9, b'Unsigned'), (10, b'Rule')]),
        ),
        migrations.AddField(
            model_name='log',
            name='status',
            field=enumerify.fields.SelectIntegerField(default=0, db_index=True, choices=[(0, b'Default'), (1, b'Sent'), (2, b'Queued'), (3, b'Scheduled'), (4, b'Rejected'), (5, b'Invalid')]),
        ),
    ]
