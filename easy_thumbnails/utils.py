from django.conf import settings
from django.utils.hashcompat import md5_constructor
from easy_thumbnails import defaults
import inspect
import math
import pickle


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
    Return a list of unique valid options for a list of image processors.
    
    """
    if processors is None:
        processors = [dynamic_import(p) for p in
                      get_setting('PROCESSORS')]
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
    Return a hex string hash for a storage object (or string containing a
    pickle of a storage object).
    
    """
    if not isinstance(storage, basestring):
        storage = pickle.dumps(storage)
    return md5_constructor(storage).hexdigest()
