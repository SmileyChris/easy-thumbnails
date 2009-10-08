from django.db import models
from easy_thumbnails import utils
import datetime
import pickle


class StorageManager(models.Manager):
    def get_or_create_storage(self, storage):
        pickled = pickle.dumps(storage)
        hash = utils.get_storage_hash(pickled)
        return self.get_or_create(hash=hash, defaults=dict(pickle=pickled))


class Storage(models.Model):
    hash = models.CharField(primary_key=True, max_length=40, editable=False)
    pickle = models.TextField(unique=True)
    
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
    name = models.CharField(max_length=255)
    modified = models.DateTimeField()

    class Meta:
        abstract = True
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.modified = datetime.datetime.now()
        super(Storage, self).save()


class Source(File):
    pass


class Thumbnail(File):
    source = models.ForeignKey(Source)
