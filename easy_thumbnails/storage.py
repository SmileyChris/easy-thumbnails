from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

from easy_thumbnails.conf import settings


def get_storage():
    # If the user has specified a custom storage backend, use it.
    from django.core.files.storage.handler import InvalidStorageError
    from django.core.files.storage import storages, default_storage

    try:
        return storages[settings.THUMBNAIL_DEFAULT_STORAGE_ALIAS]
    except InvalidStorageError:
        return default_storage


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
