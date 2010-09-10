from PIL import Image


def pil_image(source, **options):
    """
    Try to open the source file directly using PIL, ignoring any errors.

    """
    try:
        image = Image.open(source)
    except:
        return
    # Image.open() is a lazy operation, so force the load so the source file
    # can be closed again if appropriate.
    image.load()
    return image
