from django.conf import BaseSettings
from django.conf import settings as django_settings, global_settings


class AppSettings(BaseSettings):
    """
    A holder for app-specific settings.

    When :attr:`isolated` is ``False`` (the default) the holder returns
    attributes from the project's setting module, falling back to the default
    attributes provided in this module if the attribute wasn't found.
    """

    def __init__(self, isolated=False, *args, **kwargs):
        self.isolated = isolated
        super(AppSettings, self).__init__(*args, **kwargs)

    def get_isolated(self):
        return self._isolated

    def set_isolated(self, value):
        if value:
            self._isolated_overrides = BaseSettings()
        self._isolated = value

    isolated = property(get_isolated, set_isolated)

    @property
    def override_module(self):
        if self.isolated:
            return self._isolated_overrides
        return django_settings

    def __getattr__(self, attr):
        if attr == attr.upper():
            try:
                return getattr(self.override_module, attr)
            except AttributeError:
                pass
        try:
            return getattr(super(AppSettings, self), attr)
        except AttributeError:
            return getattr(global_settings, attr)

    def __setattr__(self, attr, value):
        if attr == attr.upper():
            setattr(self.override_module, attr, value)
        super(AppSettings, self).__setattr__(attr, value)


class Settings(AppSettings):
    """
    Default settings for easy-thumbnails.
    """

    THUMBNAIL_DEBUG = False

    THUMBNAIL_DEFAULT_STORAGE = 'easy_thumbnails.storage.'\
        'ThumbnailFileSystemStorage'
    THUMBNAIL_MEDIA_ROOT = ''
    THUMBNAIL_MEDIA_URL = ''

    THUMBNAIL_BASEDIR = ''
    THUMBNAIL_SUBDIR = ''
    THUMBNAIL_PREFIX = ''

    THUMBNAIL_QUALITY = 85
    THUMBNAIL_EXTENSION = 'jpg'
    THUMBNAIL_PRESERVE_EXTENSIONS = None
    THUMBNAIL_TRANSPARENCY_EXTENSION = 'png'
    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'easy_thumbnails.processors.scale_and_crop',
        'easy_thumbnails.processors.filters',
    )
    THUMBNAIL_SOURCE_GENERATORS = (
        'easy_thumbnails.source_generators.pil_image',
    )
    THUMBNAIL_CHECK_CACHE_MISS = False

    THUMBNAIL_ALIASES = None


settings = Settings()
