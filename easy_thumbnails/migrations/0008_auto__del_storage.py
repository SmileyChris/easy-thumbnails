# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'Storage'
        db.delete_table('easy_thumbnails_storage')


    def backwards(self, orm):
        
        # Adding model 'Storage'
        db.create_table('easy_thumbnails_storage', (
            ('pickle', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=40, primary_key=True, db_index=True)),
        ))
        db.send_create_signal('easy_thumbnails', ['Storage'])


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 34, 17, 1330)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage_new': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.StorageNew']"})
        },
        'easy_thumbnails.storagenew': {
            'Meta': {'object_name': 'StorageNew'},
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pickle': ('django.db.models.fields.TextField', [], {})
        },
        'easy_thumbnails.thumbnail': {
            'Meta': {'object_name': 'Thumbnail'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 34, 17, 1330)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage_new': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.StorageNew']"})
        }
    }

    complete_apps = ['easy_thumbnails']
