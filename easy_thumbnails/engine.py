import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image

from easy_thumbnails import utils
from easy_thumbnails.conf import settings


def _use_default_options(options):
    if not settings.THUMBNAIL_DEFAULT_OPTIONS:
        return options
    default_options = settings.THUMBNAIL_DEFAULT_OPTIONS.copy()
    default_options.update(options)
    return default_options


def process_image(source, processor_options, processors=None):
    """
    Process a source PIL image through a series of image processors, returning
    the (potentially) altered image.
    """
    processor_options = _use_default_options(processor_options)
    if processors is None:
        processors = [utils.dynamic_import(name)
            for name in settings.THUMBNAIL_PROCESSORS]
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


def generate_source_image(source_file, processor_options, generators=None):
    """
    Processes a source ``File`` through a series of source generators, stopping
    once a generator returns an image.

    The return value is this image instance or ``None`` if no generators
    return an image.

    If the source file cannot be opened, it will be set to ``None`` and still
    passed to the generators.
    """
    processor_options = _use_default_options(processor_options)
    was_closed = source_file.closed
    if generators is None:
        generators = [utils.dynamic_import(name)
            for name in settings.THUMBNAIL_SOURCE_GENERATORS]
    try:
        source = source_file
        try:
            source.open()
        except Exception:
            source = None
            was_closed = False
        for generator in generators:
            image = generator(source, **processor_options)
            if image:
                return image
    finally:
        if was_closed:
            source_file.close()
