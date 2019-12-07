import os

from django.core.files.base import File, ContentFile
from django.core.files.storage import (
    default_storage, Storage)
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.core.files.images import get_image_dimensions

from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils import timezone

from easy_thumbnails import engine, exceptions, models, utils, signals, storage
from easy_thumbnails.alias import aliases
from easy_thumbnails.conf import settings
from easy_thumbnails.options import ThumbnailOptions


def get_thumbnailer(obj, relative_name=None):
    """
    Get a :class:`Thumbnailer` for a source file.

    The ``obj`` argument is usually either one of the following:

        * ``FieldFile`` instance (i.e. a model instance file/image field
          property).

        * A string, which will be used as the relative name (the source will be
          set to the default storage).

        * ``Storage`` instance - the ``relative_name`` argument must also be
          provided.

    Or it could be:

        * A file-like instance - the ``relative_name`` argument must also be
          provided.

          In this case, the thumbnailer won't use or create a cached reference
          to the thumbnail (i.e. a new thumbnail will be created for every
          :meth:`Thumbnailer.get_thumbnail` call).

    If ``obj`` is a ``Thumbnailer`` instance, it will just be returned. If it's
    an object with an ``easy_thumbnails_thumbnailer`` then the attribute is
    simply returned under the assumption it is a Thumbnailer instance)
    """
    if hasattr(obj, 'easy_thumbnails_thumbnailer'):
        return obj.easy_thumbnails_thumbnailer
    if isinstance(obj, Thumbnailer):
        return obj
    elif isinstance(obj, FieldFile):
        if not relative_name:
            relative_name = obj.name
        return ThumbnailerFieldFile(obj.instance, obj.field, relative_name)

    source_storage = None

    if isinstance(obj, str):
        relative_name = obj
        obj = None

    if not relative_name:
        raise ValueError(
            "If object is not a FieldFile or Thumbnailer instance, the "
            "relative name must be provided")

    if isinstance(obj, File):
        obj = obj.file
    if isinstance(obj, Storage) or obj == default_storage:
        source_storage = obj
        obj = None

    return Thumbnailer(
        file=obj, name=relative_name, source_storage=source_storage,
        remote_source=obj is not None)


def generate_all_aliases(fieldfile, include_global):
    """
    Generate all of a file's aliases.

    :param fieldfile: A ``FieldFile`` instance.
    :param include_global: A boolean which determines whether to generate
        thumbnails for project-wide aliases in addition to field, model, and
        app specific aliases.
    """
    all_options = aliases.all(fieldfile, include_global=include_global)
    if all_options:
        thumbnailer = get_thumbnailer(fieldfile)
        for key, options in all_options.items():
            options['ALIAS'] = key
            thumbnailer.get_thumbnail(options)


def database_get_image_dimensions(file, close=False, dimensions=None):
    """
    Returns the (width, height) of an image, given ThumbnailFile.  Set
    'close' to True to close the file at the end if it is initially in an open
    state.

    Will attempt to get the dimensions from the file itself if they aren't
    in the db.
    """
    storage_hash = utils.get_storage_hash(file.storage)
    dimensions = None
    dimensions_cache = None
    try:
        thumbnail = models.Thumbnail.objects.select_related('dimensions').get(
            storage_hash=storage_hash, name=file.name)
    except models.Thumbnail.DoesNotExist:
        thumbnail = None
    else:
        try:
            dimensions_cache = thumbnail.dimensions
        except models.ThumbnailDimensions.DoesNotExist:
            dimensions_cache = None
        if dimensions_cache:
            return dimensions_cache.width, dimensions_cache.height
    dimensions = get_image_dimensions(file, close=close)
    if settings.THUMBNAIL_CACHE_DIMENSIONS and thumbnail:
        # Using get_or_create in case dimensions were created
        # while running get_image_dimensions.
        models.ThumbnailDimensions.objects.get_or_create(
            thumbnail=thumbnail,
            defaults={'width': dimensions[0], 'height': dimensions[1]})
    return dimensions


class FakeField:
    name = 'fake'

    def __init__(self, storage=None):
        if storage is None:
            storage = default_storage
        self.storage = storage

    def generate_filename(self, instance, name, *args, **kwargs):
        return name


class FakeInstance:
    def save(self, *args, **kwargs):
        pass


class ThumbnailFile(ImageFieldFile):
    """
    A thumbnailed file.

    This can be used just like a Django model instance's property for a file
    field (i.e. an ``ImageFieldFile`` object).
    """
    def __init__(self, name, file=None, storage=None, thumbnail_options=None,
                 *args, **kwargs):
        fake_field = FakeField(storage=storage)
        super().__init__(FakeInstance(), fake_field, name, *args, **kwargs)
        del self.field
        if file:
            self.file = file
        if thumbnail_options is None:
            thumbnail_options = ThumbnailOptions()
        elif not isinstance(thumbnail_options, ThumbnailOptions):
            thumbnail_options = ThumbnailOptions(thumbnail_options)
        self.thumbnail_options = thumbnail_options

    def save(self, *args, **kwargs):
        # Can't save a ``ThumbnailFile`` directly.
        raise NotImplementedError()

    def delete(self, *args, **kwargs):
        # Can't delete a ``ThumbnailFile`` directly, it doesn't have a
        # reference to the source image, so it can't update the cache. If you
        # really need to do this, do it with ``self.storage.delete`` directly.
        raise NotImplementedError()

    # Be consistant with standard behaviour, even though these methods don't
    # actually alter data any more.
    save.alters_data = True
    delete.alters_data = True

    def _get_image(self):
        """
        Get a PIL Image instance of this file.

        The image is cached to avoid the file needing to be read again if the
        function is called again.
        """
        if not hasattr(self, '_image_cache'):
            from easy_thumbnails.source_generators import pil_image
            self.image = pil_image(self)
        return self._image_cache

    def _set_image(self, image):
        """
        Set the image for this file.

        This also caches the dimensions of the image.
        """
        if image:
            self._image_cache = image
            self._dimensions_cache = image.size
        else:
            if hasattr(self, '_image_cache'):
                del self._cached_image
            if hasattr(self, '_dimensions_cache'):
                del self._dimensions_cache

    image = property(_get_image, _set_image)

    def tag(self, alt='', use_size=None, **attrs):
        """
        Return a standard XHTML ``<img ... />`` tag for this field.

        :param alt: The ``alt=""`` text for the tag. Defaults to ``''``.

        :param use_size: Whether to get the size of the thumbnail image for use
            in the tag attributes. If ``None`` (default), the size will only
            be used it if won't result in a remote file retrieval.

        All other keyword parameters are added as (properly escaped) extra
        attributes to the `img` tag.
        """
        if use_size is None:
            if getattr(self, '_dimensions_cache', None):
                use_size = True
            else:
                try:
                    self.storage.path(self.name)
                    use_size = True
                except NotImplementedError:
                    use_size = False
        attrs['alt'] = alt
        attrs['src'] = self.url
        if use_size:
            attrs.update(dict(width=self.width, height=self.height))
        attrs = ' '.join(['%s="%s"' % (key, escape(value))
                          for key, value in sorted(attrs.items())])
        return mark_safe('<img %s />' % attrs)

    def _get_file(self):
        self._require_file()
        if not hasattr(self, '_file') or self._file is None:
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, value):
        if value is not None and not isinstance(value, File):
            value = File(value)
        self._file = value
        self._committed = False

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    def open(self, mode=None, *args, **kwargs):
        if self.closed and self.name:
            mode = mode or getattr(self, 'mode', None) or 'rb'
            self.file = self.storage.open(self.name, mode)
        else:
            return super().open(mode, *args, **kwargs)

    def _get_image_dimensions(self):
        if not hasattr(self, '_dimensions_cache'):
            close = self.closed
            self.open()
            self._dimensions_cache = database_get_image_dimensions(
                self, close=close)
        return self._dimensions_cache

    def set_image_dimensions(self, thumbnail):
        """
        Set image dimensions from the cached dimensions of a ``Thumbnail``
        model instance.
        """
        try:
            dimensions = getattr(thumbnail, 'dimensions', None)
        except models.ThumbnailDimensions.DoesNotExist:
            dimensions = None
        if not dimensions:
            return False
        self._dimensions_cache = dimensions.size
        return self._dimensions_cache


class Thumbnailer(File):
    """
    A file-like object which provides some methods to generate thumbnail
    images.

    You can subclass this object and override the following properties to
    change the defaults (pulled from the default settings):

        * source_generators
        * thumbnail_processors
    """
    #: A list of source generators to use. If ``None``, will use the default
    #: generators defined in settings.
    source_generators = None
    #: A list of thumbnail processors. If ``None``, will use the default
    #: processors defined in settings.
    thumbnail_processors = None

    def __init__(self, file=None, name=None, source_storage=None,
                 thumbnail_storage=None, remote_source=False, generate=True,
                 *args, **kwargs):
        super().__init__(file, name, *args, **kwargs)
        if source_storage is None:
            source_storage = default_storage
        self.source_storage = source_storage
        if thumbnail_storage is None:
            thumbnail_storage = storage.thumbnail_default_storage
        self.thumbnail_storage = thumbnail_storage
        self.remote_source = remote_source
        self.alias_target = None
        self.generate = generate

        # Set default properties. For backwards compatibilty, check to see
        # if the attribute exists already (it could be set as a class property
        # on a subclass) before getting it from settings.
        for default in (
                'basedir', 'subdir', 'prefix', 'quality', 'extension',
                'preserve_extensions', 'transparency_extension',
                'check_cache_miss', 'high_resolution', 'highres_infix',
                'namer'):
            attr_name = 'thumbnail_%s' % default
            if getattr(self, attr_name, None) is None:
                value = getattr(settings, attr_name.upper())
                setattr(self, attr_name, value)

    def __getitem__(self, alias):
        """
        Retrieve a thumbnail matching the alias options (or raise a
        ``KeyError`` if no such alias exists).
        """
        options = aliases.get(alias, target=self.alias_target)
        if not options:
            raise KeyError(alias)
        return self.get_thumbnail(options, silent_template_exception=True)

    def get_options(self, thumbnail_options, **kwargs):
        """
        Get the thumbnail options that includes the default options for this
        thumbnailer (and the project-wide default options).
        """
        if isinstance(thumbnail_options, ThumbnailOptions):
            return thumbnail_options
        args = []
        if thumbnail_options is not None:
            args.append(thumbnail_options)
        opts = ThumbnailOptions(*args, **kwargs)
        if 'quality' not in thumbnail_options:
            opts['quality'] = self.thumbnail_quality
        return opts

    def generate_thumbnail(self, thumbnail_options, high_resolution=False,
                           silent_template_exception=False):
        """
        Return an unsaved ``ThumbnailFile`` containing a thumbnail image.

        The thumbnail image is generated using the ``thumbnail_options``
        dictionary.
        """
        thumbnail_options = self.get_options(thumbnail_options)
        orig_size = thumbnail_options['size']  # remember original size
        # Size sanity check.
        min_dim, max_dim = 0, 0
        for dim in orig_size:
            try:
                dim = int(dim)
            except (TypeError, ValueError):
                continue
            min_dim, max_dim = min(min_dim, dim), max(max_dim, dim)
        if max_dim == 0 or min_dim < 0:
            raise exceptions.EasyThumbnailsError(
                "The source image is an invalid size (%sx%s)" % orig_size)

        if high_resolution:
            thumbnail_options['size'] = (orig_size[0] * 2, orig_size[1] * 2)
        image = engine.generate_source_image(
            self, thumbnail_options, self.source_generators,
            fail_silently=silent_template_exception)
        if image is None:
            raise exceptions.InvalidImageFormatError(
                "The source file does not appear to be an image")

        thumbnail_image = engine.process_image(image, thumbnail_options,
                                               self.thumbnail_processors)
        if high_resolution:
            thumbnail_options['size'] = orig_size  # restore original size

        filename = self.get_thumbnail_name(
            thumbnail_options,
            transparent=utils.is_transparent(thumbnail_image),
            high_resolution=high_resolution)
        quality = thumbnail_options['quality']
        subsampling = thumbnail_options['subsampling']

        img = engine.save_image(
            thumbnail_image, filename=filename, quality=quality,
            subsampling=subsampling)
        data = img.read()

        thumbnail = ThumbnailFile(
            filename, file=ContentFile(data), storage=self.thumbnail_storage,
            thumbnail_options=thumbnail_options)
        thumbnail.image = thumbnail_image
        thumbnail._committed = False

        return thumbnail

    def get_thumbnail_name(self, thumbnail_options, transparent=False,
                           high_resolution=False):
        """
        Return a thumbnail filename for the given ``thumbnail_options``
        dictionary and ``source_name`` (which defaults to the File's ``name``
        if not provided).
        """
        thumbnail_options = self.get_options(thumbnail_options)
        path, source_filename = os.path.split(self.name)
        source_extension = os.path.splitext(source_filename)[1][1:]
        preserve_extensions = self.thumbnail_preserve_extensions
        if preserve_extensions and (
                preserve_extensions is True or
                source_extension.lower() in preserve_extensions):
            extension = source_extension
        elif transparent:
            extension = self.thumbnail_transparency_extension
        else:
            extension = self.thumbnail_extension
        extension = extension or 'jpg'

        prepared_opts = thumbnail_options.prepared_options()
        opts_text = '_'.join(prepared_opts)

        data = {'opts': opts_text}
        basedir = self.thumbnail_basedir % data
        subdir = self.thumbnail_subdir % data

        if isinstance(self.thumbnail_namer, str):
            namer_func = utils.dynamic_import(self.thumbnail_namer)
        else:
            namer_func = self.thumbnail_namer
        filename = namer_func(
            thumbnailer=self,
            source_filename=source_filename,
            thumbnail_extension=extension,
            thumbnail_options=thumbnail_options,
            prepared_options=prepared_opts,
        )
        if high_resolution:
            filename = self.thumbnail_highres_infix.join(
                os.path.splitext(filename))
        filename = '%s%s' % (self.thumbnail_prefix, filename)

        return os.path.join(basedir, path, subdir, filename)

    def get_existing_thumbnail(self, thumbnail_options, high_resolution=False):
        """
        Return a ``ThumbnailFile`` containing an existing thumbnail for a set
        of thumbnail options, or ``None`` if not found.
        """
        thumbnail_options = self.get_options(thumbnail_options)
        names = [
            self.get_thumbnail_name(
                thumbnail_options, transparent=False,
                high_resolution=high_resolution)]
        transparent_name = self.get_thumbnail_name(
            thumbnail_options, transparent=True,
            high_resolution=high_resolution)
        if transparent_name not in names:
            names.append(transparent_name)

        for filename in names:
            exists = self.thumbnail_exists(filename)
            if exists:
                thumbnail_file = ThumbnailFile(
                    name=filename, storage=self.thumbnail_storage,
                    thumbnail_options=thumbnail_options)
                if settings.THUMBNAIL_CACHE_DIMENSIONS:
                    # If this wasn't local storage, exists will be a thumbnail
                    # instance so we can store the image dimensions now to save
                    # a future potential query.
                    thumbnail_file.set_image_dimensions(exists)
                return thumbnail_file

    def get_thumbnail(self, thumbnail_options, save=True, generate=None,
                      silent_template_exception=False):
        """
        Return a ``ThumbnailFile`` containing a thumbnail.

        If a matching thumbnail already exists, it will simply be returned.

        By default (unless the ``Thumbnailer`` was instanciated with
        ``generate=False``), thumbnails that don't exist are generated.
        Otherwise ``None`` is returned.

        Force the generation behaviour by setting the ``generate`` param to
        either ``True`` or ``False`` as required.

        The new thumbnail image is generated using the ``thumbnail_options``
        dictionary. If the ``save`` argument is ``True`` (default), the
        generated thumbnail will be saved too.
        """
        thumbnail_options = self.get_options(thumbnail_options)
        if generate is None:
            generate = self.generate

        thumbnail = self.get_existing_thumbnail(thumbnail_options)
        if not thumbnail:
            if generate:
                thumbnail = self.generate_thumbnail(
                    thumbnail_options,
                    silent_template_exception=silent_template_exception)
                if save:
                    self.save_thumbnail(thumbnail)
            else:
                signals.thumbnail_missed.send(
                    sender=self, options=thumbnail_options,
                    high_resolution=False)

        if 'HIGH_RESOLUTION' in thumbnail_options:
            generate_high_resolution = thumbnail_options.get('HIGH_RESOLUTION')
        else:
            generate_high_resolution = self.thumbnail_high_resolution
        if generate_high_resolution:
            thumbnail.high_resolution = self.get_existing_thumbnail(
                thumbnail_options, high_resolution=True)
            if not thumbnail.high_resolution:
                if generate:
                    thumbnail.high_resolution = self.generate_thumbnail(
                        thumbnail_options, high_resolution=True,
                        silent_template_exception=silent_template_exception)
                    if save:
                        self.save_thumbnail(thumbnail.high_resolution)
                else:
                    signals.thumbnail_missed.send(
                        sender=self, options=thumbnail_options,
                        high_resolution=False)

        return thumbnail

    def save_thumbnail(self, thumbnail):
        """
        Save a thumbnail to the thumbnail_storage.

        Also triggers the ``thumbnail_created`` signal and caches the
        thumbnail values and dimensions for future lookups.
        """
        filename = thumbnail.name
        try:
            self.thumbnail_storage.delete(filename)
        except Exception:
            pass
        self.thumbnail_storage.save(filename, thumbnail)

        thumb_cache = self.get_thumbnail_cache(
            thumbnail.name, create=True, update=True)

        # Cache thumbnail dimensions.
        if settings.THUMBNAIL_CACHE_DIMENSIONS:
            dimensions_cache, created = (
                models.ThumbnailDimensions.objects.get_or_create(
                    thumbnail=thumb_cache,
                    defaults={'width': thumbnail.width,
                              'height': thumbnail.height}))
            if not created:
                dimensions_cache.width = thumbnail.width
                dimensions_cache.height = thumbnail.height
                dimensions_cache.save()

        signals.thumbnail_created.send(sender=thumbnail)

    def thumbnail_exists(self, thumbnail_name):
        """
        Calculate whether the thumbnail already exists and that the source is
        not newer than the thumbnail.

        If the source and thumbnail file storages are local, their file
        modification times are used. Otherwise the database cached modification
        times are used.
        """
        if self.remote_source:
            return False

        if utils.is_storage_local(self.source_storage):
            source_modtime = utils.get_modified_time(
                self.source_storage, self.name)
        else:
            source = self.get_source_cache()
            if not source:
                return False
            source_modtime = source.modified

        if not source_modtime:
            return False

        local_thumbnails = utils.is_storage_local(self.thumbnail_storage)
        if local_thumbnails:
            thumbnail_modtime = utils.get_modified_time(
                self.thumbnail_storage, thumbnail_name)
            if not thumbnail_modtime:
                return False
            return source_modtime <= thumbnail_modtime

        thumbnail = self.get_thumbnail_cache(thumbnail_name)
        if not thumbnail:
            return False
        thumbnail_modtime = thumbnail.modified

        if thumbnail.modified and source_modtime <= thumbnail.modified:
            return thumbnail
        return False

    def get_source_cache(self, create=False, update=False):
        if self.remote_source:
            return None
        if hasattr(self, '_source_cache') and not update:
            if self._source_cache or not create:
                return self._source_cache
        update_modified = (update or create) and timezone.now()
        self._source_cache = models.Source.objects.get_file(
            create=create, update_modified=update_modified,
            storage=self.source_storage, name=self.name,
            check_cache_miss=self.thumbnail_check_cache_miss)
        return self._source_cache

    def get_thumbnail_cache(self, thumbnail_name, create=False, update=False):
        if self.remote_source:
            return None
        source = self.get_source_cache(create=True)
        update_modified = (update or create) and timezone.now()
        return models.Thumbnail.objects.get_file(
            create=create, update_modified=update_modified,
            storage=self.thumbnail_storage, source=source, name=thumbnail_name,
            check_cache_miss=self.thumbnail_check_cache_miss)

    def open(self, mode=None):
        if self.closed:
            mode = mode or getattr(self, 'mode', None) or 'rb'
            self.file = self.source_storage.open(self.name, mode)
        else:
            self.seek(0)

    # open() doesn't alter the file's contents, but it does reset the pointer.
    open.alters_data = True


class ThumbnailerFieldFile(FieldFile, Thumbnailer):
    """
    A field file which provides some methods for generating (and returning)
    thumbnail images.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_storage = self.field.storage
        thumbnail_storage = getattr(self.field, 'thumbnail_storage', None)
        if thumbnail_storage:
            self.thumbnail_storage = thumbnail_storage
        self.alias_target = self

    def save(self, name, content, *args, **kwargs):
        """
        Save the file, also saving a reference to the thumbnail cache Source
        model.
        """
        super().save(name, content, *args, **kwargs)
        self.get_source_cache(create=True, update=True)

    def delete(self, *args, **kwargs):
        """
        Delete the image, along with any generated thumbnails.
        """
        source_cache = self.get_source_cache()
        # First, delete any related thumbnails.
        self.delete_thumbnails(source_cache)
        # Next, delete the source image.
        super().delete(*args, **kwargs)
        # Finally, delete the source cache entry.
        if source_cache and source_cache.pk is not None:
            source_cache.delete()

    delete.alters_data = True

    def delete_thumbnails(self, source_cache=None):
        """
        Delete any thumbnails generated from the source image.

        :arg source_cache: An optional argument only used for optimisation
          where the source cache instance is already known.
        :returns: The number of files deleted.
        """
        source_cache = self.get_source_cache()
        deleted = 0
        if source_cache:
            thumbnail_storage_hash = utils.get_storage_hash(
                self.thumbnail_storage)
            for thumbnail_cache in source_cache.thumbnails.all():
                # Only attempt to delete the file if it was stored using the
                # same storage as is currently used.
                if thumbnail_cache.storage_hash == thumbnail_storage_hash:
                    self.thumbnail_storage.delete(thumbnail_cache.name)
                    # Delete the cache thumbnail instance too.
                    thumbnail_cache.delete()
                    deleted += 1
        return deleted

    delete_thumbnails.alters_data = True

    def get_thumbnails(self, *args, **kwargs):
        """
        Return an iterator which returns ThumbnailFile instances.
        """
        # First, delete any related thumbnails.
        source_cache = self.get_source_cache()
        if source_cache:
            thumbnail_storage_hash = utils.get_storage_hash(
                self.thumbnail_storage)
            for thumbnail_cache in source_cache.thumbnails.all():
                # Only iterate files which are stored using the current
                # thumbnail storage.
                if thumbnail_cache.storage_hash == thumbnail_storage_hash:
                    yield ThumbnailFile(name=thumbnail_cache.name,
                                        storage=self.thumbnail_storage)

    def __getstate__(self):
        state = super().__getstate__()
        state.update({
            k: v
            for k, v in self.__dict__.items()
            if k.startswith('thumbnail') or k in ['generate', 'remote_source', 'source_storage']
        })
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__dict__['alias_target'] = self


class ThumbnailerImageFieldFile(ImageFieldFile, ThumbnailerFieldFile):
    """
    A field file which provides some methods for generating (and returning)
    thumbnail images.
    """

    def save(self, name, content, *args, **kwargs):
        """
        Save the image.

        The image will be resized down using a ``ThumbnailField`` if
        ``resize_source`` (a dictionary of thumbnail options) is provided by
        the field.
        """
        options = getattr(self.field, 'resize_source', None)
        if options:
            if 'quality' not in options:
                options['quality'] = self.thumbnail_quality
            content = Thumbnailer(content, name).generate_thumbnail(options)
            # If the generated extension differs from the original, use it
            # instead.
            orig_name, ext = os.path.splitext(name)
            generated_ext = os.path.splitext(content.name)[1]
            if generated_ext.lower() != ext.lower():
                name = orig_name + generated_ext
        super().save(name, content, *args,
                                                    **kwargs)
