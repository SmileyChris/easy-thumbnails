try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    import Image

# Constants
EXIF_ORIENTATION_TAG = 'Orientation'
EXIF_ORIENTATION_CODES = { 8:90, 3:180, 6:270 }


def _get_exif_rotation(image):
    """
    Returns the rotation angle specified in the EXIF tags or 0 if the
    Rotation tag is not found.
    """
    exif = image._getexif()
    if exif:
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)

            if decoded == EXIF_ORIENTATION_TAG:
                return EXIF_ORIENTATION_CODES.get(value, 0)

    return 0

def pil_image(source, **options):
    """
    Try to open the source file directly using PIL, ignoring any errors.
    """
    # Use a StringIO wrapper because if the source is an incomplete file like
    # object, PIL may have problems with it. For example, some image types
    # require tell and seek methods that are not present on all storage
    # File objects.
    source = StringIO(source.read())
    try:
        image = Image.open(source)

        # If EXIF rotation data is present, perform the rotation before
        # passing the data along the processing pipeline
        angle = _get_exif_rotation(image)
        if angle:
            image = image.rotate(angle)
    except:
        return
    return image
