from django.db import models
from easy_thumbnails import utils
import datetime


class FileManager(models.Manager):

    def get_file(self, storage, name, create=False, update_modified=None,
                 **kwargs):
        kwargs.update(dict(storage_hash=utils.get_storage_hash(storage),
                           name=name))
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
                return
            created = False
        if update_modified and object and not created:
            if object.modified != update_modified:
                self.filter(pk=object.pk).update(modified=update_modified)
        return object


class File(models.Model):
    storage_hash = models.CharField(max_length=40, db_index=True)
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
