from django.core.files.base import File, ContentFile
from django.core.files.storage import get_storage_class, default_storage, \
    Storage
from django.db.models.fields.files import ImageFieldFile, FieldFile
from django.utils.html import escape
from django.utils.safestring import mark_safe
from easy_thumbnails import engine, models, utils
import datetime
import os
import urllib2, shutil
from StringIO import StringIO
from django.utils.http import urlquote


DEFAULT_THUMBNAIL_STORAGE = get_storage_class(
                                        utils.get_setting('DEFAULT_STORAGE'))()


def get_thumbnailer(source, relative_name=None):
    """
    Get a thumbnailer for a source file.

    The ``source`` argument must be one of the following:

        * ``Thumbnailer`` instance

        * ``FieldFile`` instance (i.e. a model instance file/image field
          property)

        * ``File`` or ``Storage`` instance, and for both of these cases the
          ``relative_name`` argument must also be provided

        * A string, which will be used as the relative name (the source will be
          set to the default storage)

    """
    if isinstance(source, Thumbnailer):
        return source
    elif isinstance(source, FieldFile):
        if not relative_name:
            relative_name = source.name
        return ThumbnailerFieldFile(source.instance, source.field,
                                    relative_name)
    if isinstance(source, basestring) and not relative_name:
        relative_name = source
        source = default_storage
        is_storage = True
    else:
        is_storage = isinstance(source, Storage)
    if not relative_name:
        raise ValueError('If source is not a FieldFile or Thumbnailer '
                         'instance, the relative name must be provided')
    elif is_storage:
        source_image = source.open(relative_name)
        return Thumbnailer(source_image, relative_name, source_storage=source)
    elif isinstance(source, File):
        return Thumbnailer(source.file, relative_name)
    raise TypeError('Unknown source type, expected a Thumbnailer, FieldFile, '
                    'File or Storage instance.')


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
    def __init__(self, name, file=None, storage=None, *args, **kwargs):
        fake_field = FakeField(storage=storage)
        super(ThumbnailFile, self).__init__(FakeInstance(), fake_field, name,
                                            *args, **kwargs)
        del self.field
        if file:
            self.file = file

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

        If ``use_size`` isn't set, it will be default to ``True`` or ``False``
        depending on whether the file storage is local or not.

        """
        if use_size is None:
            try:
                self.field.storage.path(self.name)
                use_size = True
            except NotImplementedError:
                use_size = False
        attrs['alt'] = escape(alt)
        attrs['src'] = escape(self.url)
        if use_size:
            attrs.update(dict(width=self.width, height=self.height))
        attrs = ' '.join(['%s="%s"' % (key, escape(value))
                          for key, value in attrs.items()])
        return mark_safe('<img %s />' % attrs)

    tag = property(tag)

    def _get_file(self):
        self._require_file()
        if not hasattr(self, '_file') or self._file is None:
            self._file = self.storage.open(self.name, 'rb')
        return self._file

    def _set_file(self, value):
        if not isinstance(value, File):
            value = File(value)
        self._file = value
        self._committed = False

    def _del_file(self):
        del self._file

    file = property(_get_file, _set_file, _del_file)

    def _get_url(self):
        url = super(ThumbnailFile, self).url
        # Hack: storages should already be quoting the urls, but Django's
        # built in FileSystemStorage doesn't. We'll work around a common
        # case which shouldn't ever be used for a url (for a file) at least.
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

        * thumbnail_basedir
        * thumbnail_subdir
        * thumbnail_prefix
        * thumbnail_quality
        * thumbnail_extension

    """
    thumbnail_basedir = utils.get_setting('BASEDIR')
    thumbnail_subdir = utils.get_setting('SUBDIR')
    thumbnail_prefix = utils.get_setting('PREFIX')
    thumbnail_quality = utils.get_setting('QUALITY')
    thumbnail_extension = utils.get_setting('EXTENSION')
    thumbnail_transparency_extension = utils.get_setting(
                                                    'TRANSPARENCY_EXTENSION')

    def __init__(self, file, name=None, source_storage=None,
                 thumbnail_storage=None, *args, **kwargs):
        super(Thumbnailer, self).__init__(file, name, *args, **kwargs)
        self.source_storage = source_storage or default_storage
        self.thumbnail_storage = (thumbnail_storage or
                                  DEFAULT_THUMBNAIL_STORAGE)

    def generate_thumbnail(self, thumbnail_options):
        """
        Return a ``ThumbnailFile`` containing a thumbnail image.

        The thumbnail image is generated using the ``thumbnail_options``
        dictionary.

        """
        if not utils.is_storage_local(self.source_storage):
            # Get a local copy of the source file
            tmp_image_f = StringIO()
            orig_f = urllib2.urlopen(self.source_storage.url(self.name))
            tmp_image_f.write(orig_f.read())
            tmp_image_f.seek(0)
            self.file = tmp_image_f

        image = engine.generate_source_image(self, thumbnail_options)
        thumbnail_image = engine.process_image(image, thumbnail_options)
        quality = thumbnail_options.get('quality', self.thumbnail_quality)

        filename = self.get_thumbnail_name(thumbnail_options,
                            transparent=self.is_transparent(thumbnail_image))

        data = engine.save_image(thumbnail_image, filename=filename,
                                 quality=quality).read()

        thumbnail = ThumbnailFile(filename, ContentFile(data),
                                  storage=self.thumbnail_storage)
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
        if transparent:
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

    def get_thumbnail(self, thumbnail_options, save=True):
        """
        Return a ``ThumbnailFile`` containing a thumbnail.

        It the file already exists, it will simply be returned.

        Otherwise a new thumbnail image is generated using the
        ``thumbnail_options`` dictionary. If the ``save`` argument is ``True``
        (default), the generated thumbnail will be saved too.

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
                thumbnail = ThumbnailFile(name=filename,
                                          storage=self.thumbnail_storage)
                return thumbnail

        thumbnail = self.generate_thumbnail(thumbnail_options)
        if save:
            save_thumbnail(thumbnail, self.thumbnail_storage)
            # Ensure the right thumbnail name is used based on the transparency
            # of the image.
            filename = (self.is_transparent(thumbnail) and transparent_name or
                        opaque_name)
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
        modtime = self.get_source_modtime()
        update_modified = modtime and datetime.datetime.fromtimestamp(modtime)
        if update:
            update_modified = update_modified or datetime.datetime.utcnow()
        return models.Source.objects.get_file(
            create=create, update_modified=update_modified,
            storage=self.source_storage, name=self.name)

    def get_thumbnail_cache(self, thumbnail_name, create=False, update=False):
        modtime = self.get_thumbnail_modtime(thumbnail_name)
        update_modified = modtime and datetime.datetime.fromtimestamp(modtime)
        if update:
            update_modified = update_modified or datetime.datetime.utcnow()
        source = self.get_source_cache(create=True)
        return models.Thumbnail.objects.get_file(
            create=create, update_modified=update_modified,
            storage=self.thumbnail_storage, source=source, name=thumbnail_name)

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

    def is_transparent(self, image):
        return (image.mode == 'RGBA' or
                (image.mode == 'P' and 'transparency' in image.info))



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
        # First, delete any related thumbnails.
        source_cache = self.get_source_cache()
        if source_cache:
            thumbnail_storage_hash = utils.get_storage_hash(
                                                    self.thumbnail_storage)
            for thumbnail_cache in source_cache.thumbnails.all():
                # Only attempt to delete the file if it was stored using the
                # same storage as is currently used.
                if thumbnail_cache.storage_hash == thumbnail_storage_hash:
                    self.thumbnail_storage.delete(thumbnail_cache.name)
        # Next, delete the source image.
        super(ThumbnailerFieldFile, self).delete(*args, **kwargs)
        # Finally, delete the source cache entry (which will also delete any
        # thumbnail cache entries).
        if source_cache:
            source_cache.delete()

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

        If the thumbnail storage is local and differs from the field storage,
        save a place-holder of the source image there too. This helps to keep
        the testing of thumbnail existence as a local activity.

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
