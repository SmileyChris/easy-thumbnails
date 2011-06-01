try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image


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
    except Exception:
        return
    return image
