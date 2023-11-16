from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible
from django.utils.functional import LazyObject

from easy_thumbnails.conf import settings

def get_storage():
    # If the user has specified a custom storage backend, use it.
    try:
        from django.core.files.storage.handler import InvalidStorageError
        from django.core.files.storage import storages
        try:
            return storages[settings.THUMBNAIL_DEFAULT_STORAGE_ALIAS]
        except (InvalidStorageError):
            pass
    except (ImportError, TypeError):
        pass
    from django.core.files.storage import get_storage_class
    storage_class = get_storage_class(settings.THUMBNAIL_DEFAULT_STORAGE)
    class ThumbnailDefaultStorage(LazyObject):
        def _setup(self):
            self._wrapped = storage_class()
    return ThumbnailDefaultStorage()


@deconstructible
class ThumbnailFileSystemStorage(FileSystemStorage):
    """
    Standard file system storage.

    The default ``location`` and ``base_url`` are set to
    ``THUMBNAIL_MEDIA_ROOT`` and ``THUMBNAIL_MEDIA_URL``, falling back to the
    standard ``MEDIA_ROOT`` and ``MEDIA_URL`` if the custom settings are blank.
    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.THUMBNAIL_MEDIA_ROOT or None
        if base_url is None:
            base_url = settings.THUMBNAIL_MEDIA_URL or None
        super().__init__(location, base_url, *args, **kwargs)


thumbnail_default_storage = get_storage()
