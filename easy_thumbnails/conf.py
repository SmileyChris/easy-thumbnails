from django.conf import settings as django_settings


class BaseSettings(object):
    pass


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
                    self._changed.setdefault(
                        attr, getattr(django_settings, attr))
                except AttributeError:
                    self._added.append(attr)
            return setattr(django_settings, attr, value)
        return super(AppSettings, self).__setattr__(attr, value)


class Settings(AppSettings):
    """
    These default settings for easy-thumbnails can be specified in your Django
    project's settings module to alter the behaviour of easy-thumbnails.
    """

    THUMBNAIL_DEBUG = False
    """
    If this boolean setting is set to ``True``, display errors creating a
    thumbnail when using the :ref:`thumbnail_tag` rather than failing silently.
    """

    THUMBNAIL_DEFAULT_STORAGE = (
        'easy_thumbnails.storage.ThumbnailFileSystemStorage')
    """
    The default Django storage for *saving* generated thumbnails.
    """
    THUMBNAIL_MEDIA_ROOT = ''
    """
    Used by easy-thumbnail's default storage to locate where thumbnails are
    stored on the file system.

    If not provided, Django's standard ``MEDIA_ROOT`` setting is used.
    """
    THUMBNAIL_MEDIA_URL = ''
    """
    Used by easy-thumbnail's default storage to build the absolute URL for a
    generated thumbnail.

    If not provided, Django's standard ``MEDIA_URL`` setting is used.
    """

    THUMBNAIL_BASEDIR = ''
    """
    Save thumbnail images to a directory directly off ``MEDIA_ROOT``, still
    keeping the relative directory structure of the source image.

    For example, using the ``{% thumbnail "photos/1.jpg" 150x150 %}`` tag
    with a ``THUMBNAIL_BASEDIR`` of ``'thumbs'`` would result in the
    following thumbnail filename::

        MEDIA_ROOT + 'thumbs/photos/1_jpg_150x150_q85.jpg'
    """
    THUMBNAIL_SUBDIR = ''
    """
    Save thumbnail images to a sub-directory relative to the source image.

    For example, using the ``{% thumbnail "photos/1.jpg" 150x150 %}`` tag with
    a ``THUMBNAIL_SUBDIR`` of ``'thumbs'`` would result in the following
    thumbnail filename::

        MEDIA_ROOT + 'photos/thumbs/1_jpg_150x150_q85.jpg'
    """
    THUMBNAIL_PREFIX = ''
    """
    Prepend thumbnail filenames with the specified prefix.

    For example, using the ``{% thumbnail "photos/1.jpg" 150x150 %}`` tag with
    a ``THUMBNAIL_PREFIX`` of ``'thumbs_'`` would result in the following
    thumbnail filename::

        MEDIA_ROOT + 'photos/thumbs_1_jpg_150x150_q85.jpg'
    """

    THUMBNAIL_QUALITY = 85
    """
    The default quality level for JPG images on a scale from 1 (worst) to 95
    (best). Technically, values up to 100 are allowed, but this is not
    recommended.
    """

    THUMBNAIL_PROGRESSIVE = 100
    """
    Use progressive JPGs for thumbnails where either dimension is at least this
    many pixels.

    For example, a 90x90 image will be saved as a baseline JPG while a 728x90
    image will be saved as a progressive JPG.

    Set to ``False`` to never use progressive encoding.
    """

    THUMBNAIL_EXTENSION = 'jpg'
    """
    The type of image to save thumbnails with no transparency layer as.

    Note that changing the extension will most likely cause the
    ``THUMBNAIL_QUALITY`` setting to have no effect.
    """
    THUMBNAIL_PRESERVE_EXTENSIONS = None
    """
    To preserve specific extensions, for instance if you always want to create
    lossless PNG thumbnails from PNG sources, you can specify these extensions
    using this setting, for example::

        THUMBNAIL_PRESERVE_EXTENSIONS = ('png',)

    All extensions should be lowercase.

    Instead of a tuple, you can also set this to ``True`` in order to always
    preserve the original extension.
    """
    THUMBNAIL_TRANSPARENCY_EXTENSION = 'png'
    """
    The type of image to save thumbnails with a transparency layer (e.g. GIFs
    or transparent PNGs).
    """
    THUMBNAIL_NAMER = 'easy_thumbnails.namers.default'
    """
    The function used to generate the filename for thumbnail images.

    Four namers are included in easy_thumbnails:

    ``easy_thumbnails.namers.default``
        Descriptive filename containing the source and options like
        ``source.jpg.100x100_q80_crop_upscale.jpg``.

    ``easy_thumbnails.namers.hashed``
        Short hashed filename like ``1xedFtqllFo9.jpg``.

    ``easy_thumbnails.namers.alias``
        Filename based on ``THUMBNAIL_ALIASES`` dictionary key like ``source.jpg.medium_large.jpg``.

    ``easy_thumbnails.namers.source_hashed``
        Filename with source hashed, size, then options hashed like
        ``1xedFtqllFo9_100x100_QHCa6G1l.jpg``.

    To write a custom namer, always catch all other keyword arguments arguments
    (with \*\*kwargs). You have access to the following arguments:
    ``thumbnailer``, ``source_filename``, ``thumbnail_extension`` (does *not*
    include the ``'.'``), ``thumbnail_options``, ``prepared_options``.

    The ``thumbnail_options`` are a copy of the options dictionary used to
    build the thumbnail, ``prepared_options`` is a list of options prepared as
    text, and excluding options that shouldn't be included in the filename.
    """

    THUMBNAIL_PROCESSORS = (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'easy_thumbnails.processors.scale_and_crop',
        'easy_thumbnails.processors.filters',
        'easy_thumbnails.processors.background',
    )
    """
    Defaults to::

        THUMBNAIL_PROCESSORS = (
            'easy_thumbnails.processors.colorspace',
            'easy_thumbnails.processors.autocrop',
            'easy_thumbnails.processors.scale_and_crop',
            'easy_thumbnails.processors.filters',
            'easy_thumbnails.processors.background',
        )

    The :doc:`processors` through which the source image is run when you create
    a thumbnail.

    The order of the processors is the order in which they are sequentially
    called to process the image.
    """
    THUMBNAIL_SOURCE_GENERATORS = (
        'easy_thumbnails.source_generators.pil_image',
    )
    """
    The :doc:`source_generators` through which the base image is created from
    the source file.

    The order of the processors is the order in which they are sequentially
    tried.
    """

    THUMBNAIL_CHECK_CACHE_MISS = False
    """
    If this boolean setting is set to ``True``, and a thumbnail cannot
    be found in the database tables, we ask the storage if it has the
    thumbnail. If it does we add the row in the database, and we don't
    need to generate the thumbnail.

    Switch this to True if your easy_thumbnails_thumbnail table has been wiped
    but your storage still has the thumbnail files.
    """

    THUMBNAIL_ALIASES = None
    """
    A dictionary of predefined alias options for different targets. See the
    :ref:`usage documentation <thumbnail-aliases>` for details.
    """

    THUMBNAIL_DEFAULT_OPTIONS = None
    """
    Set this to a dictionary of options to provide as the default for all
    thumbnail calls. For example, to make all images greyscale::

        THUMBNAIL_DEFAULT_OPTIONS = {'bw': True}
    """

    THUMBNAIL_HIGH_RESOLUTION = False
    """
    Enables thumbnails for retina displays.

    Creates a version of the thumbnails in high resolution that can be used by
    a javascript layer to display higher quality thumbnails for high DPI
    displays.

    This can be overridden at a per-thumbnail level with the
    ``HIGH_RESOLUTION`` thumbnail option::

        opts = {'size': (100, 100), 'crop': True, HIGH_RESOLUTION: False}
        only_basic = get_thumbnailer(obj.image).get_thumbnail(opts)

    In a template tag, use a value of ``0`` to force the disabling of a high
    resolution version or just the option name to enable it::

        {% thumbnail obj.image 50x50 crop HIGH_RESOLUTION=0 %}  {# no hires #}
        {% thumbnail obj.image 50x50 crop HIGH_RESOLUTION %}  {# force hires #}
    """

    THUMBNAIL_HIGHRES_INFIX = '@2x'
    """
    Sets the infix used to distinguish thumbnail images for retina displays.

    Thumbnails generated for retina displays are distinguished from the
    standard resolution counterparts, by adding an infix to the filename just
    before the dot followed by the extension.

    Apple Inc., formerly suggested to use ``@2x`` as infix, but later changed
    their mind and now suggests to use ``_2x``, since this is more portable.
    """

    THUMBNAIL_CACHE_DIMENSIONS = False
    """
    Save thumbnail dimensions to the database.

    When using remote storage backends it can be a slow process to get image
    dimensions for a thumbnailed file. This option will store them in
    the database to be recalled quickly when required. Note: the old method
    still works as a fall back.
    """

    THUMBNAIL_WIDGET_OPTIONS = {'size': (80, 80)}
    """
    Default options for the
    :class:`easy_thumbnails.widgets.ImageClearableFileInput` widget.
    """

settings = Settings()
