
from south.db import db
from django.db import models
from easy_thumbnails.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Source'
        db.create_table('easy_thumbnails_source', (
            ('id', orm['easy_thumbnails.Source:id']),
            ('storage', orm['easy_thumbnails.Source:storage']),
            ('name', orm['easy_thumbnails.Source:name']),
            ('modified', orm['easy_thumbnails.Source:modified']),
        ))
        db.send_create_signal('easy_thumbnails', ['Source'])
        
        # Adding model 'Storage'
        db.create_table('easy_thumbnails_storage', (
            ('hash', orm['easy_thumbnails.Storage:hash']),
            ('pickle', orm['easy_thumbnails.Storage:pickle']),
        ))
        db.send_create_signal('easy_thumbnails', ['Storage'])
        
        # Adding model 'Thumbnail'
        db.create_table('easy_thumbnails_thumbnail', (
            ('id', orm['easy_thumbnails.Thumbnail:id']),
            ('storage', orm['easy_thumbnails.Thumbnail:storage']),
            ('name', orm['easy_thumbnails.Thumbnail:name']),
            ('modified', orm['easy_thumbnails.Thumbnail:modified']),
            ('source', orm['easy_thumbnails.Thumbnail:source']),
        ))
        db.send_create_signal('easy_thumbnails', ['Thumbnail'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Source'
        db.delete_table('easy_thumbnails_source')
        
        # Deleting model 'Storage'
        db.delete_table('easy_thumbnails_storage')
        
        # Deleting model 'Thumbnail'
        db.delete_table('easy_thumbnails_thumbnail')
        
    
    
    models = {
        'easy_thumbnails.source': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 11, 22, 21, 16, 23, 523494)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
        },
        'easy_thumbnails.storage': {
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'primary_key': 'True'}),
            'pickle': ('django.db.models.fields.TextField', [], {})
        },
        'easy_thumbnails.thumbnail': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2009, 11, 22, 21, 16, 23, 523494)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"})
        }
    }
    
    complete_apps = ['easy_thumbnails']
