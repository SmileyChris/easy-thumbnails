# encoding: utf-8
import datetime
import hashlib
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.core.files.storage import default_storage
import pickle


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting model 'Storage'
        db.delete_table('easy_thumbnails_storage')

        # Deleting field 'Source.storage'
        db.delete_column('easy_thumbnails_source', 'storage_id')

        # Adding index on 'Source', fields ['storage_hash']
        db.create_index('easy_thumbnails_source', ['storage_hash'])

        # Deleting field 'Thumbnail.storage'
        db.delete_column('easy_thumbnails_thumbnail', 'storage_id')

        # Adding index on 'Thumbnail', fields ['storage_hash']
        db.create_index('easy_thumbnails_thumbnail', ['storage_hash'])


    def backwards(self, orm):

        # Removing index on 'Thumbnail', fields ['storage_hash']
        db.delete_index('easy_thumbnails_thumbnail', ['storage_hash'])

        # Removing index on 'Source', fields ['storage_hash']
        db.delete_index('easy_thumbnails_source', ['storage_hash'])

        # Adding model 'Storage'
        db.create_table('easy_thumbnails_storage', (
            ('pickle', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=40, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('easy_thumbnails', ['Storage'])

        # Create a storage object. This may obviously not be the storage
        # object which the source / thumbnail objects actually belong to but
        # at least it lets us reverse migrate.
        storage = orm.Storage()
        storage.pickle = pickle.dumps(default_storage)
        storage.hash = hashlib.md5(storage.pickle).hexdigest()
        storage.save()

        # Adding field 'Source.storage'
        db.add_column('easy_thumbnails_source', 'storage', self.gf('django.db.models.fields.related.ForeignKey')(default=storage.pk, to=orm['easy_thumbnails.Storage']), keep_default=False)

        # Adding field 'Thumbnail.storage'
        db.add_column('easy_thumbnails_thumbnail', 'storage', self.gf('django.db.models.fields.related.ForeignKey')(default=storage.pk, to=orm['easy_thumbnails.Storage']), keep_default=False)


    models = {
        'easy_thumbnails.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 10, 6, 7, 59, 6, 528762)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        },
        'easy_thumbnails.thumbnail': {
            'Meta': {'object_name': 'Thumbnail'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 10, 6, 7, 59, 6, 528762)'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thumbnails'", 'to': "orm['easy_thumbnails.Source']"}),
            'storage_hash': ('django.db.models.fields.CharField', [], {'max_length': '40', 'db_index': 'True'})
        }
    }

    complete_apps = ['easy_thumbnails']
