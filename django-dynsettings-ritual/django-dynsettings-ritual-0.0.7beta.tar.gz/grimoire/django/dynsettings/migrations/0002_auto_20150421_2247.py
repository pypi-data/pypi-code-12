# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dynsettings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JSONDynamicSetting',
            fields=[
                ('dynamicsetting_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dynsettings.DynamicSetting')),
                ('value', jsonfield.fields.JSONField(help_text='Setting value. It must be valid JSON. This setting type is intended only for developers and users who know how to compose valid JSON values. Do not edit them unless you know what are you doing. If, by other means / database access, you or someone corrupts the value of this field, enter by the same mean and restore its original value, or just {} (open and close curly bracers) to have a valid value.', verbose_name='Value')),
            ],
            options={
                'verbose_name': 'JSON Dynamic Setting',
                'verbose_name_plural': 'JSON Dynamic Settings',
            },
            bases=('dynsettings.dynamicsetting',),
        ),
        migrations.AlterModelOptions(
            name='booleandynamicsetting',
            options={'verbose_name': 'Boolean Dynamic Setting', 'verbose_name_plural': 'Boolean Dynamic Settings'},
        ),
        migrations.AlterModelOptions(
            name='decimaldynamicsetting',
            options={'verbose_name': 'Decimal Dynamic Setting', 'verbose_name_plural': 'Decimal Dynamic Settings'},
        ),
        migrations.AlterModelOptions(
            name='dynamicsetting',
            options={'verbose_name': 'Dynamic Setting', 'verbose_name_plural': 'Dynamic Settings'},
        ),
        migrations.AlterModelOptions(
            name='integerdynamicsetting',
            options={'verbose_name': 'Integer Dynamic Setting', 'verbose_name_plural': 'Integer Dynamic Settings'},
        ),
        migrations.AlterModelOptions(
            name='longtextdynamicsetting',
            options={'verbose_name': 'Long Text Dynamic Setting', 'verbose_name_plural': 'Long Text Dynamic Settings'},
        ),
        migrations.AlterModelOptions(
            name='shorttextdynamicsetting',
            options={'verbose_name': 'Short Text Dynamic Setting', 'verbose_name_plural': 'Short Text Dynamic Settings'},
        ),
    ]
