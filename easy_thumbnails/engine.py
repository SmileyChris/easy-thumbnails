from easy_thumbnails import defaults, utils
from django.core.files.base import ContentFile
import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


DEFAULT_PROCESSORS = [utils.dynamic_import(p)
                      for p in utils.get_setting('PROCESSORS')]


def process_image(source, processor_options, processors=None):
    """
    Process a source PIL image through a series of image processors, returning
    the (potentially) altered image.
    
    """
    if processors is None:
        processors = DEFAULT_PROCESSORS
    image = source
    for processor in processors:
        image = processor(image, **processor_options)
    return image

    
def save_image(image, destination=None, format='JPEG', quality=85):
    """
    Save a PIL image.
    
    """
    if destination is None:
        destination = StringIO()
    try:
        image.save(destination, format=format, quality=quality, optimize=1)
    except IOError:
        # Try again, without optimization (PIL can't optimize an image
        # larger than ImageFile.MAXBLOCK, which is 64k by default)
        image.save(destination, format=format, quality=quality)
    if hasattr(destination, 'seek'):
        destination.seek(0)
    return destination


def get_filetype(filename, is_path=False):
    """
    Return the standardized extension based on the ``filename``.
    
    If ``is_path`` is True, try using imagemagick to determine the file type
    rather than just relying on the filename extension.
    
    """
    if is_path:
        filetype = get_filetype_magic(filename)
    if not is_path or not filetype:
        filetype = os.path.splitext(filename)[1].lower()[:1]
        if filetype == 'jpeg':
            filetype = 'jpg'
    return filetype


def get_filetype_magic(path):
    """
    Return a standardized extention by using imagemagick (or ``None`` if
    imagemagick can not be imported).
    
    """
    try:
        import magic
    except ImportError:
        return None
    
    m = magic.open(magic.MAGIC_NONE)
    m.load()
    filetype = m.file(path)
    if filetype.find('Microsoft Office Document') != -1:
        return 'doc'
    elif filetype.find('PDF document') != -1:
        return 'pdf'
    elif filetype.find('JPEG') != -1:
        return 'jpg'
    return filetype
