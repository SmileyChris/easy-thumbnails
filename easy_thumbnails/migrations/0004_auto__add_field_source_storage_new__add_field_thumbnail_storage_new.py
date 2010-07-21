# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Source.storage_new'
        db.add_column('easy_thumbnails_source', 'storage_new', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['easy_thumbnails.StorageNew'], null=True), keep_default=False)

        # Adding field 'Thumbnail.storage_new'
        db.add_column('easy_thumbnails_thumbnail', 'storage_new', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['easy_thumbnails.StorageNew'], null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Source.storage_new'
        db.delete_column('easy_thumbnails_source', 'storage_new_id')

        # Deleting field 'Thumbnail.storage_new'
        db.delete_column('easy_thumbnails_thumbnail', 'storage_new_id')


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 17, 31, 982538)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"}),
            'storage_new': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.StorageNew']", 'null': 'True'})
        },
        'easy_thumbnails.storage': {
            'Meta': {'object_name': 'Storage'},
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
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 17, 31, 982538)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"}),
            'storage_new': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.StorageNew']", 'null': 'True'})
        }
    }

    complete_apps = ['easy_thumbnails']
