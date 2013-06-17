# encoding: utf-8
import sys
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        using_mysql = db.backend_name == 'mysql'
        db.rename_table('easy_thumbnails_storagenew', 'easy_thumbnails_storage')
        if using_mysql:
            try:
                db.drop_foreign_key('easy_thumbnails_source', 'storage_new_id')
            except ValueError:
                e = sys.exc_info()[1]   # Python 2.5 compatable "as e"
                # e.g MyISAM tables don't support foreign key constraints
                print("Could not remove foreign key contraint: %s" % e)
        db.rename_column('easy_thumbnails_source', 'storage_new_id', 'storage_id')
        if using_mysql:
            try:
                db.execute('ALTER TABLE easy_thumbnails_source ADD CONSTRAINT '
                           'sourcestorage_id_fk_to_storage FOREIGN KEY (storage_id) '
                           'REFERENCES easy_thumbnails_storage(id)')
            except Exception:
                e = sys.exc_info()[1]   # Python 2.5 compatable "as e"
                print("Could not add contraint: %s" % e)

        if using_mysql:
            try:
                db.drop_foreign_key('easy_thumbnails_thumbnail', 'storage_new_id')
            except ValueError:
                e = sys.exc_info()[1]   # Python 2.5 compatable "as e"
                # e.g MyISAM tables don't support foreign key constraints
                print("Could not remove foreign key contraint: %s" % e)
        db.rename_column('easy_thumbnails_thumbnail', 'storage_new_id', 'storage_id')
        if using_mysql:
            try:
                db.execute('ALTER TABLE easy_thumbnails_thumbnail ADD CONSTRAINT '
                           'thumbnailstorage_id_fk_to_storage FOREIGN KEY (storage_id) '
                           'REFERENCES easy_thumbnails_storage(id)')
            except Exception:
                e = sys.exc_info()[1]   # Python 2.5 compatable "as e"
                print("Could not add contraint: %s" % e)


    def backwards(self, orm):
        db.rename_table('easy_thumbnails_storage', 'easy_thumbnails_storagenew')
        db.rename_column('easy_thumbnails_source', 'storage_id', 'storage_new_id')
        db.rename_column('easy_thumbnails_thumbnail', 'storage_id', 'storage_new_id')


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 35, 38, 822349)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
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
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 35, 38, 822349)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
        }
    }

    complete_apps = ['easy_thumbnails']
