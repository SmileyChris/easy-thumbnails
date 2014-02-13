# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ThumbnailDimensions'
        db.create_table(u'easy_thumbnails_thumbnaildimensions', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thumbnail', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['easy_thumbnails.Thumbnail'], unique=True)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(null=True)),
        ))
        db.send_create_signal(u'easy_thumbnails', ['ThumbnailDimensions'])


    def backwards(self, orm):
        # Deleting model 'ThumbnailDimensions'
        db.delete_table(u'easy_thumbnails_thumbnaildimensions')


    models = {
        u'easy_thumbnails.source': {
            'Meta': {'unique_together': "(('storage_hash', 'name'),)", 'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        u'easy_thumbnails.thumbnail': {
            'Meta': {'unique_together': "(('storage_hash', 'name', 'source'),)", 'object_name': 'Thumbnail'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': u"orm['easy_thumbnails.Source']"}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        u'easy_thumbnails.thumbnaildimensions': {
            'Meta': {'object_name': 'ThumbnailDimensions'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thumbnail': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['easy_thumbnails.Thumbnail']", 'unique': 'True'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['easy_thumbnails']