# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Source.name'
        db.alter_column(u'easy_thumbnails_source', 'name', self.gf('django.db.models.fields.CharField')(max_length=1023))

        # Changing field 'Thumbnail.name'
        db.alter_column(u'easy_thumbnails_thumbnail', 'name', self.gf('django.db.models.fields.CharField')(max_length=1023))

    def backwards(self, orm):

        # Changing field 'Source.name'
        db.alter_column(u'easy_thumbnails_source', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Thumbnail.name'
        db.alter_column(u'easy_thumbnails_thumbnail', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

    models = {
        u'easy_thumbnails.source': {
            'Meta': {'unique_together': "((u'storage_hash', u'name'),)", 'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'db_index': 'True'}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        u'easy_thumbnails.thumbnail': {
            'Meta': {'unique_together': "((u'storage_hash', u'name', u'source'),)", 'object_name': 'Thumbnail'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1023', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'thumbnails'", 'to': u"orm['easy_thumbnails.Source']"}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        u'easy_thumbnails.thumbnaildimensions': {
            'Meta': {'object_name': 'ThumbnailDimensions'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thumbnail': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'dimensions'", 'unique': 'True', 'to': u"orm['easy_thumbnails.Thumbnail']"}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['easy_thumbnails']
