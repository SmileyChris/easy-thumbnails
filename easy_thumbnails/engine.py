import os

from io import BytesIO, StringIO

from django.utils.module_loading import import_string

from PIL import Image

from easy_thumbnails.conf import settings
from easy_thumbnails.options import ThumbnailOptions


class NoSourceGenerator(Exception):
    """
    Exception that is raised if no source generator can process the source
    file.
    """

    def __str__(self):
        return "Tried {0} source generators with no success".format(
            len(self.args))


def process_image(source, processor_options, processors=None):
    """
    Process a source PIL image through a series of image processors, returning
    the (potentially) altered image.
    """
    processor_options = ThumbnailOptions(processor_options)
    if processors is None:
        processors = [
            import_string(name)
            for name in settings.THUMBNAIL_PROCESSORS]
    image = source
    for processor in processors:
        image = processor(image, **processor_options)
    return image


def save_pil_image(image, destination=None, filename=None, **options):
    """
    Save a PIL image.
    """
    if destination is None:
        destination = BytesIO()
    filename = filename or ''
    # Ensure plugins are fully loaded so that Image.EXTENSION is populated.
    Image.init()
    format = Image.EXTENSION.get(os.path.splitext(filename)[1].lower(), 'JPEG')
    if format in settings.THUMBNAIL_IMAGE_SAVE_OPTIONS:
        for key, value in settings.THUMBNAIL_IMAGE_SAVE_OPTIONS[format].items():
            options.setdefault(key, value)
    saved = False
    if format == 'JPEG':
        if image.mode.endswith('A'):
            # From PIL 4.2, saving an image with a transparency layer raises an
            # IOError, so explicitly remove it.
            image = image.convert(image.mode[:-1])
        if settings.THUMBNAIL_PROGRESSIVE and (
                max(image.size) >= settings.THUMBNAIL_PROGRESSIVE):
            options['progressive'] = True
        try:
            if options.pop('keep_icc_profile', False):
                options['icc_profile'] = image.info.get('icc_profile')
            image.save(destination, format=format, optimize=1, **options)
            saved = True
        except IOError:
            # Try again, without optimization (PIL can't optimize an image
            # larger than ImageFile.MAXBLOCK, which is 64k by default). This
            # shouldn't be triggered very often these days, as recent versions
            # of pillow avoid the MAXBLOCK limitation.
            pass
    else:
        if format != 'WEBP' and 'quality' in options:
            options.pop('quality')
    if not saved:
        image.save(destination, format=format, **options)
    if hasattr(destination, 'seek'):
        destination.seek(0)
    return destination


def generate_source_image(source_file, processor_options, generators=None,
                          fail_silently=True):
    """
    Processes a source ``File`` through a series of source generators, stopping
    once a generator returns an image.

    The return value is this image instance or ``None`` if no generators
    return an image.

    If the source file cannot be opened, it will be set to ``None`` and still
    passed to the generators.
    """
    processor_options = ThumbnailOptions(processor_options)
    # Keep record of whether the source file was originally closed. Not all
    # file-like objects provide this attribute, so just fall back to False.
    was_closed = getattr(source_file, 'closed', False)
    if generators is None:
        generators = [
            import_string(name)
            for name in settings.THUMBNAIL_SOURCE_GENERATORS]
    exceptions = []
    try:
        for generator in generators:
            source = source_file
            # First try to open the file.
            try:
                source.open()
            except Exception:
                # If that failed, maybe the file-like object doesn't support
                # reopening so just try seeking back to the start of the file.
                try:
                    source.seek(0)
                except Exception:
                    source = None
            try:
                image = generator(source, **processor_options)
            except Exception as e:
                if not fail_silently:
                    if len(generators) == 1:
                        raise
                    exceptions.append(e)
                image = None
            if image:
                return image
    finally:
        # Attempt to close the file if it was closed originally (but fail
        # silently).
        if was_closed:
            try:
                source_file.close()
            except Exception:
                pass
    if exceptions and not fail_silently:
        raise NoSourceGenerator(*exceptions)


def save_svg_image(image, destination=None, filename=None, **options):
    """
    Save a SVG image.
    """
    from easy_thumbnails.VIL import Image

    if destination is None:
        destination = StringIO()
    image.save(destination, format='SVG', **options)
    if hasattr(destination, 'seek'):
        destination.seek(0)
    return destination
