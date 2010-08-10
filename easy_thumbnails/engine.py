try:
    from PIL import Image
except ImportError:
    import Image
from easy_thumbnails import utils
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


def save_image(image, destination=None, filename=None, **options):
    """
    Save a PIL image.
    
    """
    if destination is None:
        destination = StringIO()
    filename = filename or ''
    format = Image.EXTENSION.get(os.path.splitext(filename)[1], 'JPEG')
    if format == 'JPEG':
        options.setdefault('quality', 85)
        try:
            image.save(destination, format=format, optimize=1, **options)
        except IOError:
            # Try again, without optimization (PIL can't optimize an image
            # larger than ImageFile.MAXBLOCK, which is 64k by default)
            pass
    image.save(destination, format=format, **options)
    if hasattr(destination, 'seek'):
        destination.seek(0)
    return destination
