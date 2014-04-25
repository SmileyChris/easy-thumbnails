# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def copy(self, orm, OldModel, NewModel):
        old_field = new_field = None
        for field in orm.Source._meta.fields:
            if isinstance(field, models.ForeignKey):
                if field.rel.to == orm.Storage:
                    old_field = field
                elif field.rel.to == orm.StorageNew:
                    new_field = field
        assert old_field and new_field
        for storage in OldModel.objects.all():
            new_storage = NewModel()
            for key in [f.attname for f in OldModel._meta.fields]:
                setattr(new_storage, key, getattr(storage, key))
            new_storage.save()
            filter_kwargs = {old_field.name: storage}
            update_kwargs = {new_field.name: new_storage}
            for Model in (orm.Source, orm.Thumbnail):
                Model.objects.filter(**filter_kwargs).update(**update_kwargs)
    
    
    def forwards(self, orm):
        self.copy(orm, orm.Storage, orm.StorageNew)


    def backwards(self, orm):
        self.copy(orm, orm.StorageNew, orm.Storage)


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 7, 21, 4, 17, 31, 982538)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']", 'null': 'True'}),
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
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']", 'null': 'True'}),
            'storage_new': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.StorageNew']", 'null': 'True'})
        }
    }

    complete_apps = ['easy_thumbnails']
