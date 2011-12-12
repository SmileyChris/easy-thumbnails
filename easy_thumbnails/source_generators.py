try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image

from easy_thumbnails import utils


def pil_image(source, **options):
    """
    Try to open the source file directly using PIL, ignoring any errors.
    """
    # Use a StringIO wrapper because if the source is an incomplete file like
    # object, PIL may have problems with it. For example, some image types
    # require tell and seek methods that are not present on all storage
    # File objects.
    if not source:
        return
    source = StringIO(source.read())
    try:
        image = Image.open(source)
    except Exception:
        return
    # If EXIF orientation data is present, perform any required reorientation
    # before passing the data along the processing pipeline.
    image = utils.exif_orientation(image)
    return image
