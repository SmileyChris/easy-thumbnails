# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models
from django.core.files.storage import default_storage
from django.utils.hashcompat import md5_constructor
import pickle

class Migration(DataMigration):
    """
    Migrate storage hashes.

    """

    def get_storage_hash(self, storage):
        """
        Return a hex string hash for a storage object (or string containing a
        pickle of a storage object).
        
        """
        try:
            # Make sure that pickle is getting a string, since it can choke
            # with unicode.
            storage_obj = pickle.loads(str(self.pickle))
        except:
            # We need to return some storage, and if there's an exception then
            # it is most likely the default_storage (since that fails with a
            # recursion error due to LazyObject "awesomeness").
            storage_obj = default_storage
        storage_cls = storage_obj.__class__
        name = '%s.%s' % (storage_cls.__module__, storage_cls.__name__)
        return md5_constructor(name).hexdigest()

    def forwards(self, orm):
        "Write your forwards methods here."
        for storage in orm.Storage.objects.all():
            storage_hash = self.get_storage_hash(storage)
            orm.Source.objects.filter(storage=storage).update(
                                        storage_hash=storage_hash)
            orm.Thumbnail.objects.filter(storage=storage).update(
                                        storage_hash=storage_hash)
            
    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 8, 0, 32, 41, 855399)'}),
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
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 9, 8, 0, 32, 41, 855399)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['easy_thumbnails.Storage']"}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        }
    }

    complete_apps = ['easy_thumbnails']
