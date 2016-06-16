# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import otree.models.varsmixin
import otree.db.models
import otree.common_internal


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedGroupWaitPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('page_index', models.PositiveIntegerField()),
                ('session_pk', models.PositiveIntegerField()),
                ('group_pk', models.PositiveIntegerField()),
                ('after_all_players_arrive_run', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CompletedSubsessionWaitPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('page_index', models.PositiveIntegerField()),
                ('session_pk', models.PositiveIntegerField()),
                ('after_all_players_arrive_run', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ExpectedRoomParticipant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('room_name', models.CharField(max_length=50)),
                ('participant_label', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FailedSessionCreation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('pre_create_id', models.CharField(db_index=True, max_length=100)),
                ('message', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='GlobalSingleton',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('locked', otree.db.models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PageCompletion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('app_name', models.CharField(max_length=300)),
                ('page_index', models.PositiveIntegerField()),
                ('page_name', models.CharField(max_length=300)),
                ('time_stamp', models.PositiveIntegerField()),
                ('seconds_on_page', models.PositiveIntegerField()),
                ('subsession_pk', models.PositiveIntegerField()),
                ('participant_pk', models.PositiveIntegerField()),
                ('session_pk', models.PositiveIntegerField()),
                ('auto_submitted', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='PageTimeout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('participant_pk', models.PositiveIntegerField()),
                ('page_index', models.PositiveIntegerField()),
                ('expiration_time', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('vars', otree.db.models.JSONField(null=True, default=dict)),
                ('exclude_from_data_analysis', otree.db.models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)),
                ('time_started', otree.db.models.DateTimeField(null=True)),
                ('mturk_assignment_id', otree.db.models.CharField(null=True, max_length=50)),
                ('mturk_worker_id', otree.db.models.CharField(null=True, max_length=50)),
                ('start_order', otree.db.models.PositiveIntegerField(db_index=True, null=True)),
                ('label', otree.db.models.CharField(null=True, max_length=50)),
                ('_index_in_subsessions', otree.db.models.PositiveIntegerField(null=True, default=0)),
                ('_index_in_pages', otree.db.models.PositiveIntegerField(db_index=True, null=True, default=0)),
                ('id_in_session', otree.db.models.PositiveIntegerField(null=True)),
                ('_waiting_for_ids', otree.db.models.CharField(null=True, max_length=300)),
                ('code', otree.db.models.CharField(unique=True, null=True, default=otree.common_internal.random_chars_8, max_length=16)),
                ('last_request_succeeded', otree.db.models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], verbose_name='Health of last server request')),
                ('visited', otree.db.models.BooleanField(db_index=True, choices=[(True, 'Yes'), (False, 'No')], default=False)),
                ('ip_address', otree.db.models.GenericIPAddressField(null=True)),
                ('_last_page_timestamp', otree.db.models.PositiveIntegerField(null=True)),
                ('_last_request_timestamp', otree.db.models.PositiveIntegerField(null=True)),
                ('is_on_wait_page', otree.db.models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)),
                ('_current_page_name', otree.db.models.CharField(null=True, verbose_name='page', max_length=200)),
                ('_current_app_name', otree.db.models.CharField(null=True, verbose_name='app', max_length=200)),
                ('_round_number', otree.db.models.PositiveIntegerField(null=True)),
                ('_current_form_page_url', otree.db.models.URLField(null=True)),
                ('_max_page_index', otree.db.models.PositiveIntegerField(null=True)),
                ('_is_auto_playing', otree.db.models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)),
            ],
            options={
                'ordering': ['pk'],
            },
            bases=(otree.models.varsmixin._SaveTheChangeWithCustomFieldSupport, models.Model),
        ),
        migrations.CreateModel(
            name='ParticipantLockModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('participant_code', models.CharField(unique=True, max_length=16)),
                ('locked', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantRoomVisit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('room_name', models.CharField(max_length=50)),
                ('participant_label', models.CharField(max_length=200)),
                ('tab_unique_id', models.CharField(unique=True, max_length=20)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantToPlayerLookup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('participant_pk', models.PositiveIntegerField()),
                ('page_index', models.PositiveIntegerField()),
                ('app_name', models.CharField(max_length=300)),
                ('player_pk', models.PositiveIntegerField()),
                ('url', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='RoomToSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('room_name', models.CharField(unique=True, max_length=255)),
                ('session_pk', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('vars', otree.db.models.JSONField(null=True, default=dict)),
                ('config', otree.db.models.JSONField(null=True, default=dict)),
                ('label', otree.db.models.CharField(blank=True, null=True, help_text='For internal record-keeping', max_length=300)),
                ('experimenter_name', otree.db.models.CharField(blank=True, null=True, help_text='For internal record-keeping', max_length=300)),
                ('code', otree.db.models.CharField(unique=True, null=True, default=otree.common_internal.random_chars_8, max_length=16)),
                ('time_scheduled', otree.db.models.DateTimeField(blank=True, help_text='For internal record-keeping', null=True)),
                ('time_started', otree.db.models.DateTimeField(null=True)),
                ('mturk_HITId', otree.db.models.CharField(blank=True, null=True, help_text='Hit id for this session on MTurk', max_length=300)),
                ('mturk_HITGroupId', otree.db.models.CharField(blank=True, null=True, help_text='Hit id for this session on MTurk', max_length=300)),
                ('mturk_qualification_type_id', otree.db.models.CharField(blank=True, null=True, help_text='Qualification type that is assigned to each worker taking hit', max_length=300)),
                ('mturk_num_participants', otree.db.models.IntegerField(null=True, help_text='Number of participants on MTurk', default=-1)),
                ('mturk_sandbox', otree.db.models.BooleanField(help_text='Should this session be created in mturk sandbox?', choices=[(True, 'Yes'), (False, 'No')], default=True)),
                ('archived', otree.db.models.BooleanField(db_index=True, choices=[(True, 'Yes'), (False, 'No')], default=False)),
                ('comment', otree.db.models.TextField(blank=True, null=True)),
                ('_anonymous_code', otree.db.models.CharField(db_index=True, null=True, default=otree.common_internal.random_chars_10, max_length=8)),
                ('special_category', otree.db.models.CharField(db_index=True, null=True, max_length=20)),
                ('_pre_create_id', otree.db.models.CharField(db_index=True, null=True, max_length=300)),
            ],
            options={
                'ordering': ['pk'],
            },
            bases=(otree.models.varsmixin._SaveTheChangeWithCustomFieldSupport, models.Model),
        ),
        migrations.CreateModel(
            name='StubModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='participanttoplayerlookup',
            unique_together=set([('participant_pk', 'page_index')]),
        ),
        migrations.AlterIndexTogether(
            name='participanttoplayerlookup',
            index_together=set([('participant_pk', 'page_index')]),
        ),
        migrations.AddField(
            model_name='participant',
            name='session',
            field=otree.db.models.ForeignKey(to='otree.Session'),
        ),
        migrations.AlterIndexTogether(
            name='pagetimeout',
            index_together=set([('participant_pk', 'page_index')]),
        ),
        migrations.AlterUniqueTogether(
            name='completedsubsessionwaitpage',
            unique_together=set([('page_index', 'session_pk')]),
        ),
        migrations.AlterIndexTogether(
            name='completedsubsessionwaitpage',
            index_together=set([('page_index', 'session_pk')]),
        ),
        migrations.AlterUniqueTogether(
            name='completedgroupwaitpage',
            unique_together=set([('page_index', 'session_pk', 'group_pk')]),
        ),
        migrations.AlterIndexTogether(
            name='completedgroupwaitpage',
            index_together=set([('page_index', 'session_pk', 'group_pk')]),
        ),
        migrations.AlterIndexTogether(
            name='participant',
            index_together=set([('session', 'mturk_worker_id', 'mturk_assignment_id')]),
        ),
    ]
