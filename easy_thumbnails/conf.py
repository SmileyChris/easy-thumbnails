from django.conf import settings as django_settings
try:
    from django.conf import BaseSettings
except ImportError:  # Django <= 1.2
    from django.conf import Settings as BaseSettings


class AppSettings(BaseSettings):
    """
    A holder for app-specific settings.

    When :attr:`isolated` is ``False`` (the default) the holder returns
    attributes from the project's setting module, falling back to the default
    attributes provided in this module if the attribute wasn't found.
    """

    def __init__(self, isolated=False, *args, **kwargs):
        self.isolated = isolated
        self._changed = {}
        self._added = []
        super(AppSettings, self).__init__(*args, **kwargs)

    def get_isolated(self):
        return self._isolated

    def set_isolated(self, value):
        if value:
            self._isolated_overrides = BaseSettings()
        self._isolated = value

    isolated = property(get_isolated, set_isolated)

    def revert(self):
        """
        Revert any changes made to settings.
        """
        for attr, value in self._changed.items():
            setattr(django_settings, attr, value)
        for attr in self._added:
            delattr(django_settings, attr)
        self._changed = {}
        self._added = []
        if self.isolated:
            self._isolated_overrides = BaseSettings()

    def __getattribute__(self, attr):
        if attr == attr.upper():
            if self.isolated:
                try:
                    return getattr(self._isolated_overrides, attr)
                except AttributeError:
                    pass
            else:
                try:
                    return getattr(django_settings, attr)
                except AttributeError:
                    pass
        try:
            return super(AppSettings, self).__getattribute__(attr)
        except AttributeError:
            if not self.isolated:
                raise
            return getattr(django_settings, attr)

    def __setattr__(self, attr, value):
        if attr == attr.upper():
            if self.isolated:
                try:
                    super(AppSettings, self).__getattribute__(attr)
                except AttributeError:
                    pass
                else:
                    # Set the app setting to an isolated overrides that gets
                    # checked before the project's settings.
                    return setattr(self._isolated_overrides, attr, value)
            # Keep track of any project settings changes so they can be
            # reverted.
            if attr not in self._added:
                try:
                    self._changed.setdefault(attr,
                        getattr(django_settings, attr))
                except AttributeError:
                    self._added.append(attr)
            return setattr(django_settings, attr, value)
        return super(AppSettings, self).__setattr__(attr, value)


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

    THUMBNAIL_DEFAULT_OPTIONS = None


settings = Settings()
