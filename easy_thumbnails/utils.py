import inspect
import math
import datetime
import os

from django.utils.functional import LazyObject

try:
    from hashlib import md5 as md5_constructor
except ImportError:
    from django.utils.hashcompat import md5_constructor

try:
    from PIL import Image
except ImportError:
    import Image

try:
    from django.utils import timezone
    now = timezone.now

    def make_time_zone_aware(dt):
        if getattr(settings, 'USE_TZ', False):
            default_timezone = timezone.get_default_timezone()
            return timezone.make_aware(dt, default_timezone)
        return dt

except ImportError:
    now = datetime.datetime.now
    make_time_zone_aware = lambda dt: dt

from easy_thumbnails.conf import settings


def image_entropy(im):
    """
    Calculate the entropy of an image. Used for "smart cropping".
    """
    if not isinstance(im, Image.Image):
        # Can only deal with PIL images. Fall back to a constant entropy.
        return 0
    hist = im.histogram()
    hist_size = float(sum(hist))
    hist = [h / hist_size for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])


def dynamic_import(import_string):
    """
    Dynamically import a module or object.
    """
    # Use rfind rather than rsplit for Python 2.3 compatibility.
    lastdot = import_string.rfind('.')
    if lastdot == -1:
        return __import__(import_string, {}, {}, [])
    module_name, attr = import_string[:lastdot], import_string[lastdot + 1:]
    parent_module = __import__(module_name, {}, {}, [attr])
    return getattr(parent_module, attr)


def valid_processor_options(processors=None):
    """
    Return a list of unique valid options for a list of image processors
    (and/or source generators)
    """
    if processors is None:
        processors = [
            dynamic_import(p) for p in
            settings.THUMBNAIL_PROCESSORS +
            settings.THUMBNAIL_SOURCE_GENERATORS]
    valid_options = set(['size', 'quality'])
    for processor in processors:
        args = inspect.getargspec(processor)[0]
        # Add all arguments apart from the first (the source image).
        valid_options.update(args[1:])
    return list(valid_options)


def is_storage_local(storage):
    """
    Check to see if a file storage is local.
    """
    try:
        storage.path('test')
    except NotImplementedError:
        return False
    return True


def get_storage_hash(storage):
    """
    Return a hex string hash for a storage object (or string containing
    'full.path.ClassName' referring to a storage object).
    """
    # If storage is wrapped in a lazy object we need to get the real thing.
    if isinstance(storage, LazyObject):
        if storage._wrapped is None:
            storage._setup()
        storage = storage._wrapped
    if not isinstance(storage, basestring):
        storage_cls = storage.__class__
        storage = '%s.%s' % (storage_cls.__module__, storage_cls.__name__)
    return md5_constructor(storage).hexdigest()


def is_transparent(image):
    """
    Check to see if an image is transparent.
    """
    if not isinstance(image, Image.Image):
        # Can only deal with PIL images, fall back to the assumption that that
        # it's not transparent.
        return False
    return (image.mode in ('RGBA', 'LA') or
            (image.mode == 'P' and 'transparency' in image.info))


def exif_orientation(im):
    """
    Rotate and/or flip an image to respect the image's EXIF orientation data.
    """
    try:
        exif = im._getexif()
    except (AttributeError, IndexError, KeyError, IOError):
        exif = None
    if exif:
        orientation = exif.get(0x0112)
        if orientation == 2:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            im = im.rotate(180)
        elif orientation == 4:
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            im = im.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            im = im.rotate(-90)
        elif orientation == 7:
            im = im.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            im = im.rotate(90)
    return im


def get_modified_time(storage, name):
    """
    Get modified time from storage if the storage implements modified_time.
    Fall back to using os.path (assumes a FS-based storage) for backwards-compatibility
    """
    try:
        try:
            return storage.modified_time(name)
        except AttributeError: # older storage interface didn't have "modified_time"
            path = storage.path(name)
            return datetime.datetime.fromtimestamp(os.path.getmtime(path))
    except OSError:
        return 0
    except NotImplementedError:
        return None
