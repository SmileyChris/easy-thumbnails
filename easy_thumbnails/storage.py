from django.core.files.storage import FileSystemStorage
from easy_thumbnails import utils


class ThumbnailFileSystemStorage(FileSystemStorage):
    """
    Standard file system storage.

    The default ``location`` and ``base_url`` are set to
    ``THUMBNAIL_MEDIA_ROOT`` and ``THUMBNAIL_MEDIA_URL``, falling back to the
    standard ``MEDIA_ROOT`` and ``MEDIA_URL`` if the custom settings are blank.
    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        location = utils.get_setting('MEDIA_ROOT', override=location) or None
        base_url = utils.get_setting('MEDIA_URL', override=base_url) or None
        super(ThumbnailFileSystemStorage, self).__init__(location, base_url,
                                                         *args, **kwargs)
