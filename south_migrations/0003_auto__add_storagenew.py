# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'StorageNew'
        db.create_table('easy_thumbnails_storagenew', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('pickle', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('easy_thumbnails', ['StorageNew'])


    def backwards(self, orm):
        
        # Deleting model 'StorageNew'
        db.delete_table('easy_thumbnails_storagenew')


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 11, 43, 389353)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
        },
        'easy_thumbnails.storage': {
            'Meta': {'object_name': 'Storage', 'db_table': "'easy_thumbnails_storage_tmp'"},
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True', 'db_index': 'True'}),
            'pickle': ('django.db.models.fields.TextField', [], {})
        },
        'easy_thumbnails.storagenew': {
            'Meta': {'object_name': 'StorageNew'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'pickle': ('django.db.models.fields.TextField', [], {})
        },
        'easy_thumbnails.thumbnail': {
            'Meta': {'object_name': 'Thumbnail'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 11, 43, 389353)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
        }
    }

    complete_apps = ['easy_thumbnails']
