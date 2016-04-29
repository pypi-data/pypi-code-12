# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Outlet'
        db.create_table(u'outlets_outlet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['outlets.OutletCountry'])),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('phone', self.gf('phonenumber_field.modelfields.PhoneNumberField')(max_length=128, null=True, blank=True)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('lat', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('lon', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
        ))
        db.send_create_signal(u'outlets', ['Outlet'])

        # Adding model 'OutletCountry'
        db.create_table(u'outlets_outletcountry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=64)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'outlets', ['OutletCountry'])


    def backwards(self, orm):
        # Deleting model 'Outlet'
        db.delete_table(u'outlets_outlet')

        # Deleting model 'OutletCountry'
        db.delete_table(u'outlets_outletcountry')


    models = {
        u'outlets.outlet': {
            'Meta': {'ordering': "('position', 'name')", 'object_name': 'Outlet'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['outlets.OutletCountry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'lon': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'phone': ('phonenumber_field.modelfields.PhoneNumberField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'outlets.outletcountry': {
            'Meta': {'ordering': "('position', 'name')", 'object_name': 'OutletCountry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['outlets']
