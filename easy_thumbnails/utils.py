from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.hashcompat import md5_constructor
from easy_thumbnails import defaults
import inspect
import math


def image_entropy(im):
    """
    Calculate the entropy of an image. Used for "smart cropping".
    """
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
        processors = [dynamic_import(p) for p in get_setting('PROCESSORS') +
                      get_setting('SOURCE_GENERATORS')]
    valid_options = set(['size', 'quality'])
    for processor in processors:
        args = inspect.getargspec(processor)[0]
        # Add all arguments apart from the first (the source image).
        valid_options.update(args[1:])
    return list(valid_options)


def get_setting(setting, override=None):
    """
    Get a thumbnail setting from Django settings module, falling back to the
    default.

    If override is not None, it will be used instead of the setting.
    """
    if override is not None:
        return override
    if hasattr(settings, 'THUMBNAIL_%s' % setting):
        return getattr(settings, 'THUMBNAIL_%s' % setting)
    else:
        return getattr(defaults, setting)


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
