# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import vr.server.fields
import vr.server.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Used in release name.  Good app names are short and use no spaces or dashes (underscores are OK).', unique=True, max_length=50, validators=[vr.server.models.validate_app_name])),
                ('repo_url', models.CharField(max_length=200)),
                ('repo_type', models.CharField(max_length=10, choices=[(b'git', b'git'), (b'hg', b'hg')])),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'deployment_app',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=50)),
                ('file', models.FileField(max_length=200, null=True, upload_to=b'builds', blank=True)),
                ('file_md5', models.CharField(max_length=32, null=True, blank=True)),
                ('compile_log', models.FileField(max_length=200, null=True, upload_to=b'builds', blank=True)),
                ('start_time', models.DateTimeField(null=True)),
                ('end_time', models.DateTimeField(null=True)),
                ('status', models.CharField(default=b'pending', max_length=20, choices=[(b'pending', b'Pending'), (b'started', b'Started'), (b'success', b'Success'), (b'failed', b'Failed'), (b'expired', b'Expired')])),
                ('hash', models.CharField(max_length=32, null=True, blank=True)),
                ('env_yaml', vr.server.fields.YAMLDictField(help_text=b'YAML dict of env vars from buildpack', null=True, blank=True)),
                ('buildpack_url', models.CharField(max_length=200, null=True, blank=True)),
                ('buildpack_version', models.CharField(max_length=50, null=True, blank=True)),
                ('app', models.ForeignKey(to='server.App')),
            ],
            options={
                'ordering': ['-id'],
                'db_table': 'deployment_build',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildPack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('repo_url', models.CharField(unique=True, max_length=200)),
                ('repo_type', models.CharField(default=b'git', max_length=10, choices=[(b'git', b'git'), (b'hg', b'hg')])),
                ('desc', models.TextField(null=True, blank=True)),
                ('order', models.IntegerField()),
            ],
            options={
                'ordering': ['order'],
                'db_table': 'deployment_buildpack',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('config_yaml', vr.server.fields.YAMLDictField(help_text=b'Config for settings.yaml. Must be valid YAML dict.', null=True, blank=True)),
                ('env_yaml', vr.server.fields.YAMLDictField(help_text=b'Environment variables. Must be valid YAML dict.', null=True, blank=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'deployment_configingredient',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField()),
                ('apps', models.ManyToManyField(to='server.App')),
                ('editors', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeploymentLogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=50, choices=[(b'build', b'Build'), (b'release', b'Release'), (b'deployment', b'Deployment')])),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('message', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
                'db_table': 'deployment_deploymentlogentry',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'deployment_host',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OSImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('file', models.FileField(null=True, upload_to=vr.server.models.build_os_image_path, blank=True)),
                ('file_md5', models.CharField(max_length=32, null=True, editable=False)),
                ('base_image_url', models.CharField(max_length=200, null=True, blank=True)),
                ('base_image_name', models.CharField(max_length=200, null=True, blank=True)),
                ('provisioning_script_url', models.CharField(max_length=200, null=True, blank=True)),
                ('build_log', models.FileField(null=True, upload_to=b'images', blank=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'deployment_os_image',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OSStack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('desc', models.TextField()),
                ('base_image_url', models.CharField(max_length=200, null=True, blank=True)),
                ('provisioning_script', models.FileField(null=True, upload_to=b'provisioning_scripts', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'deployment_os_stack',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PortLock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('port', models.IntegerField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('host', models.ForeignKey(to='server.Host')),
            ],
            options={
                'db_table': 'deployment_portlock',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('config_yaml', vr.server.fields.YAMLDictField(help_text=b'Config for settings.yaml. Must be valid YAML dict.', null=True, blank=True)),
                ('env_yaml', vr.server.fields.YAMLDictField(help_text=b'YAML dict of env vars to be set at runtime', null=True, blank=True)),
                ('volumes', vr.server.fields.YAMLListField(help_text=b'YAML list of directory,mountpoint pairs to be exposed inside the container. E.g. "- [/var/data, /data]"', null=True, blank=True)),
                ('hash', models.CharField(max_length=32, null=True, blank=True)),
                ('run_as', models.CharField(default=b'nobody', max_length=32)),
                ('mem_limit', models.CharField(help_text=b'Maximum amount of RAM for the app. E.g. 256M', max_length=32, null=True, blank=True)),
                ('memsw_limit', models.CharField(help_text=b'Maximum amount of RAM and swap for the app. E.g. 1G', max_length=32, null=True, blank=True)),
                ('build', models.ForeignKey(to='server.Build')),
            ],
            options={
                'ordering': ['-id'],
                'db_table': 'deployment_release',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Squad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'deployment_squad',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Swarm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('config_name', models.CharField(help_text=b"Short name like 'prod' or 'europe' to distinguish between deployments of the same app. Must be filesystem-safe, with no dashes or spaces.", max_length=50)),
                ('proc_name', models.CharField(max_length=50)),
                ('size', models.IntegerField(default=1, help_text=b'The number of procs in the swarm')),
                ('pool', models.CharField(help_text=b'The name of the pool in the load balancer (omit prefix)', max_length=50, null=True, blank=True)),
                ('balancer', models.CharField(blank=True, max_length=50, null=True, choices=[(b'default', b'default')])),
                ('config_yaml', vr.server.fields.YAMLDictField(help_text=b'Config for settings.yaml. Must be valid YAML dict.', null=True, blank=True)),
                ('env_yaml', vr.server.fields.YAMLDictField(help_text=b'YAML dict of env vars to be set at runtime', null=True, blank=True)),
                ('volumes', vr.server.fields.YAMLListField(help_text=b'YAML list of directory,mountpoint pairs to be exposed inside the container. E.g. "- [/var/data, /data]"', null=True, blank=True)),
                ('run_as', models.CharField(default=b'nobody', max_length=32)),
                ('mem_limit', models.CharField(help_text=b'Maximum amount of RAM for the app. E.g. 256M', max_length=32, null=True)),
                ('memsw_limit', models.CharField(help_text=b'Maximum amount of RAM and swap for the app. E.g. 1G', max_length=32, null=True)),
                ('app', models.ForeignKey(to='server.App', null=True)),
                ('config_ingredients', models.ManyToManyField(help_text=b'Optional config shared with other swarms.', to='server.ConfigIngredient', blank=True)),
                ('release', models.ForeignKey(to='server.Release')),
                ('squad', models.ForeignKey(to='server.Squad')),
            ],
            options={
                'ordering': ['app__name', 'config_name', 'proc_name'],
                'db_table': 'deployment_swarm',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('app', models.ForeignKey(to='server.App')),
            ],
            options={
                'db_table': 'deployment_tag',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField()),
                ('hostname', models.CharField(max_length=200)),
                ('procname', models.CharField(max_length=200)),
                ('passed', models.BooleanField(default=False)),
                ('testcount', models.IntegerField(default=0)),
                ('results', models.TextField()),
            ],
            options={
                'db_table': 'deployment_testresult',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ['-start'],
                'db_table': 'deployment_testrun',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('default_dashboard', models.ForeignKey(related_name='def+', blank=True, to='server.Dashboard', null=True)),
                ('quick_dashboards', models.ManyToManyField(related_name='quick+', to='server.Dashboard', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='testresult',
            name='run',
            field=models.ForeignKey(related_name='tests', to='server.TestRun'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='swarm',
            unique_together=set([('app', 'config_name', 'squad', 'proc_name')]),
        ),
        migrations.AlterUniqueTogether(
            name='portlock',
            unique_together=set([('host', 'port')]),
        ),
        migrations.AddField(
            model_name='osimage',
            name='stack',
            field=models.ForeignKey(blank=True, to='server.OSStack', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='host',
            name='squad',
            field=models.ForeignKey(related_name='hosts', blank=True, to='server.Squad', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='build',
            name='os_image',
            field=models.ForeignKey(blank=True, to='server.OSImage', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='app',
            name='buildpack',
            field=models.ForeignKey(blank=True, to='server.BuildPack', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='app',
            name='stack',
            field=models.ForeignKey(blank=True, to='server.OSStack', null=True),
            preserve_default=True,
        ),
    ]
