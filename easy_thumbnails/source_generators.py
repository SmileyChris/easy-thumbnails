from io import BytesIO

from PIL import Image, ImageFile
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

    with Image.open(source) as image:
        # Fully load the image now to catch any problems with the image contents.
        try:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            image.load()
        finally:
            ImageFile.LOAD_TRUNCATED_IMAGES = False

    if exif_orientation:
        image = utils.exif_orientation(image)
    return image
