# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Source.storage_hash'
        db.add_column('easy_thumbnails_source', 'storage_hash', self.gf('django.db.models.fields.CharField')(default='', max_length=40), keep_default=False)

        # Adding field 'Thumbnail.storage_hash'
        db.add_column('easy_thumbnails_thumbnail', 'storage_hash', self.gf('django.db.models.fields.CharField')(default='', max_length=40), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Source.storage_hash'
        db.delete_column('easy_thumbnails_source', 'storage_hash')

        # Deleting field 'Thumbnail.storage_hash'
        db.delete_column('easy_thumbnails_thumbnail', 'storage_hash')


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 8, 0, 31, 16, 27396)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'easy_thumbnails.storage': {
            'Meta': {'object_name': 'Storage'},
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pickle': ('django.db.models.fields.TextField', [], {})
        },
        'easy_thumbnails.thumbnail': {
            'Meta': {'object_name': 'Thumbnail'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 8, 0, 31, 16, 27396)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['easy_thumbnails']
