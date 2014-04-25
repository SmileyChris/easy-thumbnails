try:
    from cStringIO import cStringIO as BytesIO
except ImportError:
    from django.utils.six import BytesIO

try:
    from PIL import Image
except ImportError:
    import Image

from easy_thumbnails import utils


def pil_image(source, exif_orientation=True, **options):
    """
    Try to open the source file directly using PIL, ignoring any errors.

    exif_orientation

        If EXIF orientation data is present, perform any required reorientation
        before passing the data along the processing pipeline.

    """
    # Use a BytesIO wrapper because if the source is an incomplete file like
    # object, PIL may have problems with it. For example, some image types
    # require tell and seek methods that are not present on all storage
    # File objects.
    if not source:
        return
    source = BytesIO(source.read())

    image = Image.open(source)
    # Fully load the image now to catch any problems with the image contents.
    try:
        # An "Image file truncated" exception can occur for some images that
        # are still mostly valid -- we'll swallow the exception.
        image.load()
    except IOError:
        pass
    # Try a second time to catch any other potential exceptions.
    image.load()

    if exif_orientation:
        image = utils.exif_orientation(image)
    return image
