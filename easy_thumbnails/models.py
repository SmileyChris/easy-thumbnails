from django.db import models
from easy_thumbnails import utils
import datetime
import pickle


def get_storage(storage):
    pickled = pickle.dumps(storage)
    hash = utils.get_storage_hash(pickled)
    return Storage.objects.get_or_create(hash=hash,
                                         defaults=dict(pickle=pickled))[0]


def _get(model, get_kwargs, create=False, update=False):
    if create:
        object, created = model.objects.get_or_create(**get_kwargs)[1]
    else:
        try:
            object = model.objects.get(**get_kwargs)
        except model.DoesNotExist:
            object = None
        created = False
    if update and not created:
        object.save()
    return object
    

def get_source(thumbnailer, create=False, update=False):
    storage = get_storage(thumbnailer.source_storage)
    kwargs = dict(storage=storage, name=thumbnailer.name)
    return _get(Source, kwargs, create=create, update=update)


def get_thumbnail(thumbnailer, name, source=None, create=False, update=False):
    source = source or get_source(thumbnailer, create=True)
    storage = get_storage(thumbnailer.thumbnail_storage)
    kwargs = dict(storage=storage, source=source, name=name)
    return _get(Thumbnail, kwargs, create=create, update=update)


class Storage(models.Model):
    hash = models.CharField(primary_key=True, max_length=40, editable=False)
    pickle = models.TextField(unique=True)
    
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
    source = models.ForeignKey(Source, related_name='thumbnails')
