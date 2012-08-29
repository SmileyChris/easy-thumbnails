from django.core.files.base import File, ContentFile
from django.core.files.storage import get_storage_class, default_storage, \
    Storage
from django.db.models.fields.files import ImageFieldFile, FieldFile
import os

from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.http import urlquote

from easy_thumbnails import engine, exceptions, models, utils, signals
from easy_thumbnails.alias import aliases
from easy_thumbnails.conf import settings


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

    if isinstance(obj, basestring):
        relative_name = obj
        obj = None

    if not relative_name:
        raise ValueError("If object is not a FieldFile or Thumbnailer "
            "instance, the relative name must be provided")

    if isinstance(obj, File):
        obj = obj.file
    if isinstance(obj, Storage) or obj == default_storage:
        source_storage = obj
        obj = None

    return Thumbnailer(file=obj, name=relative_name,
        source_storage=source_storage, remote_source=obj is not None)


def save_thumbnail(thumbnail_file, storage):
    """
    Save a thumbnailed file, returning the saved relative file name.
    """
    filename = thumbnail_file.name
    if storage.exists(filename):
        try:
            storage.delete(filename)
        except:
            pass
    return storage.save(filename, thumbnail_file)


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
        for options in all_options.values():
            thumbnailer.get_thumbnail(options)


class FakeField(object):
    name = 'fake'

    def __init__(self, storage=None):
        self.storage = storage or default_storage

    def generate_filename(self, instance, name, *args, **kwargs):
        return name


class FakeInstance(object):
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
        super(ThumbnailFile, self).__init__(FakeInstance(), fake_field, name,
            *args, **kwargs)
        del self.field
        if file:
            self.file = file
        self.thumbnail_options = thumbnail_options

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

        :param use_size: Whether to get the size of the thumbnail image for use in
            the tag attributes. If ``None`` (default), it will be ``True`` or
            ``False`` depending on whether the file storage is local or not.

        All other keyword parameters are added as (properly escaped) extra
        attributes to the `img` tag.
        """
        if use_size is None:
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

    def _get_url(self):
        """
        Return the full url of this file.

        .. note:: storages should already be quoting the urls, but Django's
                  built in ``FileSystemStorage`` doesn't.
                  ``ThumbnailFieldFile`` works around a common case of the file
                  containing a ``#``, which shouldn't ever be used for a url.
        """
        url = super(ThumbnailFile, self).url
        if '#' in url:
            url = urlquote(url)
        return url

    url = property(_get_url)

    def open(self, mode=None, *args, **kwargs):
        if self.closed and self.name:
            self.file = self.storage.open(self.name, mode or self.mode or 'rb')
        else:
            return super(ThumbnailFile, self).open(mode, *args, **kwargs)


class Thumbnailer(File):
    """
    A file-like object which provides some methods to generate thumbnail
    images.

    You can subclass this object and override the following properties to
    change the defaults (pulled from the default settings):

        * source_generators
        * thumbnail_processors
    """
    source_generators = None
    thumbnail_processors = None

    def __init__(self, file=None, name=None, source_storage=None,
            thumbnail_storage=None, remote_source=False, generate=True, *args,
            **kwargs):
        super(Thumbnailer, self).__init__(file, name, *args, **kwargs)
        self.source_storage = source_storage or default_storage
        if not thumbnail_storage:
            thumbnail_storage = get_storage_class(
                settings.THUMBNAIL_DEFAULT_STORAGE)()
        self.thumbnail_storage = thumbnail_storage
        self.remote_source = remote_source
        self.alias_target = None
        self.generate = generate

        # Set default properties. For backwards compatibilty, check to see
        # if the attribute exists already (it could be set as a class property
        # on a subclass) before getting it from settings.
        for default in ('basedir', 'subdir', 'prefix', 'quality', 'extension',
                'preserve_extensions', 'transparency_extension',
                'check_cache_miss'):
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
        return self.get_thumbnail(options)

    def generate_source_image(self, thumbnail_options):
        return engine.generate_source_image(self, thumbnail_options,
                                            self.source_generators)

    def generate_thumbnail(self, thumbnail_options):
        """
        Return an unsaved ``ThumbnailFile`` containing a thumbnail image.

        The thumbnail image is generated using the ``thumbnail_options``
        dictionary.
        """
        image = self.generate_source_image(thumbnail_options)
        if image is None:
            raise exceptions.InvalidImageFormatError(
                "The source file does not appear to be an image")

        thumbnail_image = engine.process_image(image, thumbnail_options,
                                               self.thumbnail_processors)
        quality = thumbnail_options.get('quality', self.thumbnail_quality)

        filename = self.get_thumbnail_name(thumbnail_options,
            transparent=utils.is_transparent(thumbnail_image))

        data = engine.save_image(thumbnail_image, filename=filename,
            quality=quality).read()

        thumbnail = ThumbnailFile(filename, file=ContentFile(data),
            storage=self.thumbnail_storage,
            thumbnail_options=thumbnail_options)
        thumbnail.image = thumbnail_image
        thumbnail._committed = False

        return thumbnail

    def get_thumbnail_name(self, thumbnail_options, transparent=False):
        """
        Return a thumbnail filename for the given ``thumbnail_options``
        dictionary and ``source_name`` (which defaults to the File's ``name``
        if not provided).
        """
        path, source_filename = os.path.split(self.name)
        source_extension = os.path.splitext(source_filename)[1][1:]
        filename = '%s%s' % (self.thumbnail_prefix, source_filename)
        if self.thumbnail_preserve_extensions == True or  \
            (self.thumbnail_preserve_extensions and  \
            source_extension.lower() in self.thumbnail_preserve_extensions):
                extension = source_extension
        elif transparent:
            extension = self.thumbnail_transparency_extension
        else:
            extension = self.thumbnail_extension
        extension = extension or 'jpg'

        thumbnail_options = thumbnail_options.copy()
        size = tuple(thumbnail_options.pop('size'))
        quality = thumbnail_options.pop('quality', self.thumbnail_quality)
        initial_opts = ['%sx%s' % size, 'q%s' % quality]

        opts = thumbnail_options.items()
        opts.sort()   # Sort the options so the file name is consistent.
        opts = ['%s' % (v is not True and '%s-%s' % (k, v) or k)
                for k, v in opts if v]

        all_opts = '_'.join(initial_opts + opts)

        data = {'opts': all_opts}
        basedir = self.thumbnail_basedir % data
        subdir = self.thumbnail_subdir % data

        filename_parts = [filename]
        if ('%(opts)s' in self.thumbnail_basedir or
            '%(opts)s' in self.thumbnail_subdir):
            if extension != source_extension:
                filename_parts.append(extension)
        else:
            filename_parts += [all_opts, extension]
        filename = '.'.join(filename_parts)

        return os.path.join(basedir, path, subdir, filename)

    def get_thumbnail(self, thumbnail_options, save=True, generate=None):
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
        opaque_name = self.get_thumbnail_name(thumbnail_options,
                                              transparent=False)
        transparent_name = self.get_thumbnail_name(thumbnail_options,
                                                   transparent=True)
        if opaque_name == transparent_name:
            names = (opaque_name,)
        else:
            names = (opaque_name, transparent_name)
        for filename in names:
            if self.thumbnail_exists(filename):
                return ThumbnailFile(name=filename,
                    storage=self.thumbnail_storage,
                    thumbnail_options=thumbnail_options)

        if generate is None:
            generate = self.generate
        if not generate:
            signals.thumbnail_missed.send(sender=self,
                options=thumbnail_options)
            return

        thumbnail = self.generate_thumbnail(thumbnail_options)
        if save:
            save_thumbnail(thumbnail, self.thumbnail_storage)
            signals.thumbnail_created.send(sender=thumbnail)
            # Ensure the right thumbnail name is used based on the transparency
            # of the image.
            filename = (utils.is_transparent(thumbnail.image) and
                        transparent_name or opaque_name)
            self.get_thumbnail_cache(filename, create=True, update=True)

        return thumbnail

    def thumbnail_exists(self, thumbnail_name):
        """
        Calculate whether the thumbnail already exists and that the source is
        not newer than the thumbnail.

        If both the source and thumbnail file storages are local, their
        file modification times are used. Otherwise the database cached
        modification times are used.
        """
        if self.remote_source:
            return False
        # Try to use the local file modification times first.
        source_modtime = self.get_source_modtime()
        thumbnail_modtime = self.get_thumbnail_modtime(thumbnail_name)
        # The thumbnail modification time will be 0 if there was an OSError,
        # in which case it will still be used (but always return False).
        if source_modtime and thumbnail_modtime is not None:
            return thumbnail_modtime and source_modtime <= thumbnail_modtime
        # Fall back to using the database cached modification times.
        source = self.get_source_cache()
        if not source:
            return False
        thumbnail = self.get_thumbnail_cache(thumbnail_name)
        return thumbnail and source.modified <= thumbnail.modified

    def get_source_cache(self, create=False, update=False):
        if self.remote_source:
            return None
        modtime = self.get_source_modtime()
        update_modified = modtime and utils.fromtimestamp(modtime)
        if update:
            update_modified = update_modified or utils.now()
        return models.Source.objects.get_file(
            create=create, update_modified=update_modified,
            storage=self.source_storage, name=self.name,
            check_cache_miss=self.thumbnail_check_cache_miss)

    def get_thumbnail_cache(self, thumbnail_name, create=False, update=False):
        if self.remote_source:
            return None
        modtime = self.get_thumbnail_modtime(thumbnail_name)
        update_modified = modtime and utils.fromtimestamp(modtime)
        if update:
            update_modified = update_modified or utils.now()
        source = self.get_source_cache(create=True)
        return models.Thumbnail.objects.get_file(
            create=create, update_modified=update_modified,
            storage=self.thumbnail_storage, source=source, name=thumbnail_name,
            check_cache_miss=self.thumbnail_check_cache_miss)

    def get_source_modtime(self):
        try:
            path = self.source_storage.path(self.name)
            return os.path.getmtime(path)
        except OSError:
            return 0
        except NotImplementedError:
            return None

    def get_thumbnail_modtime(self, thumbnail_name):
        try:
            path = self.thumbnail_storage.path(thumbnail_name)
            return os.path.getmtime(path)
        except OSError:
            return 0
        except NotImplementedError:
            return None

    def open(self, mode=None):
        if self.closed:
            self.file = self.source_storage.open(self.name,
                mode or self.mode or 'rb')
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
        super(ThumbnailerFieldFile, self).__init__(*args, **kwargs)
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
        super(ThumbnailerFieldFile, self).save(name, content, *args, **kwargs)
        self.get_source_cache(create=True, update=True)

    def delete(self, *args, **kwargs):
        """
        Delete the image, along with any generated thumbnails.
        """
        source_cache = self.get_source_cache()
        # First, delete any related thumbnails.
        self.delete_thumbnails(source_cache)
        # Next, delete the source image.
        super(ThumbnailerFieldFile, self).delete(*args, **kwargs)
        # Finally, delete the source cache entry.
        if source_cache:
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
            if not 'quality' in options:
                options['quality'] = self.thumbnail_quality
            content = Thumbnailer(content).generate_thumbnail(options)
        super(ThumbnailerImageFieldFile, self).save(name, content, *args,
                                                    **kwargs)
