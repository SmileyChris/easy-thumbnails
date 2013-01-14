import inspect
import math
import datetime

from django.utils.functional import LazyObject

try:
    from hashlib import md5 as md5_constructor
except ImportError:
    from django.utils.hashcompat import md5_constructor

try:
    from PIL import Image
except ImportError:
    import Image

try:
    from django.utils import timezone
    now = timezone.now

    def fromtimestamp(timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        if getattr(settings, 'USE_TZ', False):
            default_timezone = timezone.get_default_timezone()
            return timezone.make_aware(dt, default_timezone)
        return dt

except ImportError:
    now = datetime.datetime.now
    fromtimestamp = datetime.datetime.fromtimestamp

from easy_thumbnails.conf import settings
from functools import partial
import logging
import select

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from threading import Thread

PIPE_BUFFER = getattr(select, "PIPE_BUF", 512)  # select.PIPE_BUF only >= 2.7
logger = logging.getLogger(__name__)


def image_entropy(im):
    """
    Calculate the entropy of an image. Used for "smart cropping".
    """
    if not isinstance(im, Image.Image):
        # Can only deal with PIL images. Fall back to a constant entropy.
        return 0
    hist = im.histogram()
    hist_size = float(sum(hist))
    hist = [h / hist_size for h in hist]
    return -sum([p * math.log(p, 2) for p in hist if p != 0])


def dynamic_import(import_string):
    """
    Dynamically import a module or object.
    """
    # Use rfind rather than rsplit for Python 2.3 compatibility.
    lastdot = import_string.rfind('.')
    if lastdot == -1:
        return __import__(import_string, {}, {}, [])
    module_name, attr = import_string[:lastdot], import_string[lastdot + 1:]
    parent_module = __import__(module_name, {}, {}, [attr])
    return getattr(parent_module, attr)


def valid_processor_options(processors=None):
    """
    Return a list of unique valid options for a list of image processors
    (and/or source generators)
    """
    if processors is None:
        processors = [dynamic_import(p) for p in
            settings.THUMBNAIL_PROCESSORS +
            settings.THUMBNAIL_SOURCE_GENERATORS]
    valid_options = set(['size', 'quality'])
    for processor in processors:
        args = inspect.getargspec(processor)[0]
        # Add all arguments apart from the first (the source image).
        valid_options.update(args[1:])
    return list(valid_options)


def is_storage_local(storage):
    """
    Check to see if a file storage is local.
    """
    try:
        storage.path('test')
    except NotImplementedError:
        return False
    return True


def get_storage_hash(storage):
    """
    Return a hex string hash for a storage object (or string containing
    'full.path.ClassName' referring to a storage object).
    """
    # If storage is wrapped in a lazy object we need to get the real thing.
    if isinstance(storage, LazyObject):
        if storage._wrapped is None:
            storage._setup()
        storage = storage._wrapped
    if not isinstance(storage, basestring):
        storage_cls = storage.__class__
        storage = '%s.%s' % (storage_cls.__module__, storage_cls.__name__)
    return md5_constructor(storage).hexdigest()


def is_transparent(image):
    """
    Check to see if an image is transparent.
    """
    if not isinstance(image, Image.Image):
        # Can only deal with PIL images, fall back to the assumption that that
        # it's not transparent.
        return False
    return (image.mode in ('RGBA', 'LA') or
            (image.mode == 'P' and 'transparency' in image.info))


def exif_orientation(im):
    """
    Rotate and/or flip an image to respect the image's EXIF orientation data.
    """
    try:
        exif = im._getexif()
    except (AttributeError, IndexError, KeyError, IOError):
        exif = None
    if exif:
        orientation = exif.get(0x0112)
        if orientation == 2:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            im = im.rotate(180)
        elif orientation == 4:
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            im = im.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            im = im.rotate(-90)
        elif orientation == 7:
            im = im.rotate(90).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            im = im.rotate(90)
    return im


def consume(fd):
    """
    Reads from a file into a StringIO.

    Python blocks reads from files, so a thread is used to read into a
    StringIO. See http://stackoverflow.com/a/4896288/253686 for further
    explanation

    Don't use the returned `StringIO` until the thread has finished.

    :returns: `tuple` of ``(StringIO, Thread)``
    """
    def worker(fd, buf):
        read = partial(fd.read, PIPE_BUFFER)
        for chunk in iter(read, b''):
            buf.write(chunk)
        fd.close()

    output = StringIO()
    thread = Thread(target=worker, args=(fd, output))
    thread.daemon = True  # thread dies with Python
    thread.start()
    return (output, thread)


def communicate(process, input):
    """
    Communicate with process, chunking *input* to stdin.

    This differs from `subprocess.communicate` in that *input* is a file-like
    stream, not a string. The return values are also `StringIO`, not strings.

    :param process: `Popen` object
    :param   input: file-like stream
    :returns: `tuple` of ``(stdout, stderr)`` (each is a `StringIO`)

    As with `subprocess.communicate`, *stderr* and *stdout* are buffered in
    memory, and are `None` unless `subprocess.PIPE` was specified in `Popen`.
    """
    consumers = []
    error, output = None, None

    if process.stderr is not None:
        (error, consumer) = consume(process.stderr)
        consumers.append(consumer)

    if process.stdout is not None:
        (output, consumer) = consume(process.stdout)
        consumers.append(consumer)

    try:
        read = partial(input.read, PIPE_BUFFER)
        for buf in iter(read, b''):
            try:
                process.stdin.write(buf)
            except:
                # The process has closed stdin, it's probably finished executing
                break
        else:
            process.stdin.close()
    except:
        # If we can't read the input, something's gone horrible wrong.
        logger.exception("Failed to read from input stream, skipping...")
        process.kill()
        return

    # read everything from stdout/stderr
    for consumer in consumers:
        consumer.join()

    # rewind
    if output is not None:
        output.seek(0)
    if error is not None:
        error.seek(0)

    process.wait()  # populate process.returncode

    return (output, error)
