
from south.db import db
from django.db import models
from easy_thumbnails.models import *

class Migration:
    
    def forwards(self, orm):
        db.create_index('easy_thumbnails_source', ['name'])
        db.create_index('easy_thumbnails_thumbnail', ['name'])
        db.create_index('easy_thumbnails_storage', ['hash'])
    
    
    def backwards(self, orm):
        db.delete_index('easy_thumbnails_source', ['name'])
        db.delete_index('easy_thumbnails_thumbnail', ['name'])
        db.delete_index('easy_thumbnails_storage', ['hash'])
    
    
    models = {
        'easy_thumbnails.source': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 11, 22, 21, 17, 49, 7917)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
        },
        'easy_thumbnails.storage': {
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True', 'db_index': 'True'}),
            'pickle': ('django.db.models.fields.TextField', [], {})
        },
        'easy_thumbnails.thumbnail': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 11, 22, 21, 17, 49, 7917)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
        }
    }
    
    complete_apps = ['easy_thumbnails']
