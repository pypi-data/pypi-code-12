# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings

class Migration(SchemaMigration):

    depends_on = []

    def forwards(self, orm):

        # Deleting model 'Keyword'
        db.delete_table('core_keyword')


    def backwards(self, orm):

        # Adding model 'Keyword'
        db.create_table('core_keyword', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('core', ['Keyword'])


    models = {

    }

    complete_apps = ['core']
