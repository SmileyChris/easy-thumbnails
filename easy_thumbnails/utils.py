import hashlib
import inspect
import math

from django.utils import timezone
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

from PIL import Image
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


def valid_processor_options(processors=None):
    """
    Return a list of unique valid options for a list of image processors
    (and/or source generators)
    """
    if processors is None:
        processors = [
            import_string(p) for p in
            tuple(settings.THUMBNAIL_PROCESSORS) +
            tuple(settings.THUMBNAIL_SOURCE_GENERATORS)]
    valid_options = set(['size', 'quality', 'subsampling'])
    for processor in processors:
        args = inspect.getfullargspec(processor)[0]
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
    if not isinstance(storage, str):
        storage_cls = storage.__class__
        storage = '%s.%s' % (storage_cls.__module__, storage_cls.__name__)
    return hashlib.md5(storage.encode('utf8')).hexdigest()


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


def is_progressive(image):
    """
    Check to see if an image is progressive.
    """
    if not isinstance(image, Image.Image):
        # Can only check PIL images for progressive encoding.
        return False
    return ('progressive' in image.info) or ('progression' in image.info)


def exif_orientation(im):
    """
    Rotate and/or flip an image to respect the image's EXIF orientation data.
    """
    # Check Pillow version and use right constant
    try:
        # Pillow >= 9.1.0
        Image__Transpose = Image.Transpose
    except AttributeError:
        # Pillow < 9.1.0
        Image__Transpose = Image

    try:
        exif = im._getexif()
    except Exception:
        # There are many ways that _getexif fails, we're just going to blanket
        # cover them all.
        exif = None
    if exif:
        orientation = exif.get(0x0112)
        if orientation == 2:
            im = im.transpose(Image__Transpose.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            im = im.transpose(Image__Transpose.ROTATE_180)
        elif orientation == 4:
            im = im.transpose(Image__Transpose.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            im = im.transpose(Image__Transpose.ROTATE_270) \
                   .transpose(Image__Transpose.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            im = im.transpose(Image__Transpose.ROTATE_270)
        elif orientation == 7:
            im = im.transpose(Image__Transpose.ROTATE_90) \
                   .transpose(Image__Transpose.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            im = im.transpose(Image__Transpose.ROTATE_90)
    return im


def get_modified_time(storage, name):
    """
    Get modified time from storage, ensuring the result is a timezone-aware
    datetime.
    """
    try:
        modified_time = storage.get_modified_time(name)
    except OSError:
        return 0
    except NotImplementedError:
        return None
    if modified_time and timezone.is_naive(modified_time):
        if getattr(settings, 'USE_TZ', False):
            default_timezone = timezone.get_default_timezone()
            return timezone.make_aware(modified_time, default_timezone)
    return modified_time
