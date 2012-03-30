from django.db import models

from easy_thumbnails import utils, signal_handlers


class FileManager(models.Manager):

    def get_file(self, storage, name, create=False, update_modified=None,
                 check_cache_miss=False, **kwargs):
        kwargs.update(dict(storage_hash=utils.get_storage_hash(storage),
                           name=name))
        if create:
            if update_modified:
                defaults = kwargs.setdefault('defaults', {})
                defaults['modified'] = update_modified
            object, created = self.get_or_create(**kwargs)
        else:
            created = False
            kwargs.pop('defaults', None)
            try:
                object = self.get(**kwargs)
            except self.model.DoesNotExist:

                if check_cache_miss and storage.exists(name):
                    # File already in storage, update cache
                    object = self.create(**kwargs)
                    created = True
                else:
                    return

        if update_modified and object and not created:
            if object.modified != update_modified:
                self.filter(pk=object.pk).update(modified=update_modified)
        return object


class File(models.Model):
    storage_hash = models.CharField(max_length=40, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    modified = models.DateTimeField(default=utils.now)

    objects = FileManager()

    class Meta:
        abstract = True
        unique_together = (('storage_hash', 'name'),)

    def __unicode__(self):
        return self.name


class Source(File):
    pass


class Thumbnail(File):
    source = models.ForeignKey(Source, related_name='thumbnails')

    class Meta:
        unique_together = (('storage_hash', 'name', 'source'),)


models.signals.pre_save.connect(signal_handlers.find_uncommitted_filefields)
models.signals.post_save.connect(signal_handlers.signal_committed_filefields)
