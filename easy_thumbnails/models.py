from django.db import models
from easy_thumbnails import utils
import datetime
import pickle


class StorageManager(models.Manager):
    _storage_cache = {}
    
    def get_storage(self, storage):
        pickled = pickle.dumps(storage)
        hash = utils.get_storage_hash(pickled)
        if hash not in self._storage_cache:
            self._storage_cache[hash] = self.get_or_create(hash=hash,
                                            defaults=dict(pickle=pickled))[0]
        return self._storage_cache[hash]


class FileManager(models.Manager):
    def get_file(self, storage, name, create=False, update_modified=None,
                 **kwargs):
        if not isinstance(storage, Storage):
            storage = Storage.objects.get_storage(storage)
        kwargs.update(dict(storage=storage, name=name))
        if create:
            if update_modified:
                defaults = kwargs.setdefault('defaults', {})
                defaults['modified'] = update_modified
            object, created = self.get_or_create(**kwargs)
        else:
            kwargs.pop('defaults', None)
            try:
                object = self.get(**kwargs)
            except self.model.DoesNotExist:
                object = None
            created = False
        if update_modified and object and not created:
            if object.modified != update_modified:
                object.modified = update_modified
                object.save()
        return object


class Storage(models.Model):
    hash = models.CharField(primary_key=True, max_length=40, editable=False,
                            db_index=True)
    pickle = models.TextField()

    objects = StorageManager()

    def save(self, *args, **kwargs):
        self.hash = utils.get_storage_hash(self.pickle)
        super(Storage, self).save()

    def decode(self):
        """
        Returned the unpickled storage object, or ``None`` if an error occurs
        while unpickling.
          
        """
        try:
            return pickle.loads(self.pickle)
        except:
            pass


class File(models.Model):
    storage = models.ForeignKey(Storage)
    name = models.CharField(max_length=255, db_index=True)
    modified = models.DateTimeField(default=datetime.datetime.utcnow())

    objects = FileManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name


class Source(File):
    pass


class Thumbnail(File):
    source = models.ForeignKey(Source, related_name='thumbnails')
