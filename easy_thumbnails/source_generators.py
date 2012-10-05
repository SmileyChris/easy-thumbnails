try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image

from easy_thumbnails import utils
import logging
import select
import subprocess


logger = logging.getLogger(__name__)


def pil_image(source, exif_orientation=True, **options):
    """
    Try to open the source file directly using PIL, ignoring any errors.

    exif_orientation

        If EXIF orientation data is present, perform any required reorientation
        before passing the data along the processing pipeline.

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
        # Fully load the image now to catch any problems with the image
        # contents.
        image.load()
    except Exception:
        return

    if exif_orientation:
        image = utils.exif_orientation(image)
    return image


def ffmpeg(source, **options):
    """
    Try and use ffmpeg to process the source, ignoring any errors.

    Requires the ``ffmpeg`` command to be installed and on the ``PATH``.
    """
    # Take the first frame, scale it to display aspect ratio (DAR), output as
    # an image.
    proc = subprocess.Popen(["ffmpeg", "-i", "-", "-vframes", "1",
                             "-vf", "scale=ih*dar:ih", "-f", "image2",
                             "-"],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (stdout, stderr) = utils.communicate(proc, source)
    if proc.returncode != 0:
        logger.warning("ffmpeg failed with return code %d" % proc.returncode)
        logger.debug(stderr)
        return
    return pil_image(stdout)
