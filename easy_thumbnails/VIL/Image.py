import builtins
from pathlib import Path

from django.core.files import File
from django.utils.functional import cached_property

from reportlab.graphics import renderSVG
from reportlab.lib.colors import Color

from svglib.svglib import svg2rlg


class Image:
    """
    Attempting to be compatible with PIL's Image, but suitable for reportlab's SVGCanvas.
    """
    def __init__(self, size=(300, 300)):
        assert isinstance(size, (list, tuple)) and len(size) == 2 \
            and isinstance(size[0], (int, float)) and isinstance(size[1], (int, float)), \
            "Expected `size` as tuple with two floats or integers"
        self.canvas = renderSVG.SVGCanvas(size=size, useClip=True)
        self.mode = None

    @property
    def size(self):
        return self.width, self.height

    @cached_property
    def width(self):
        try:
            return float(self.canvas.svg.getAttribute('width'))
        except ValueError:
            return self.getbbox()[2]

    @cached_property
    def height(self):
        try:
            return float(self.canvas.svg.getAttribute('height'))
        except ValueError:
            return self.getbbox()[3]

    def getbbox(self):
        """
        Calculates the bounding box of the non-zero regions in the image.

        :returns: The bounding box is returned as a 4-tuple defining the
           left, upper, right, and lower pixel coordinate.
        """
        return tuple(float(b) for b in self.canvas.svg.getAttribute('viewBox').split())

    def resize(self, size, **kwargs):
        """
        :param size: The requested size in pixels, as a 2-tuple: (width, height).
        :returns: The resized :py:class:`easy_thumbnails.VIL.Image.Image` object.
        """
        copy = Image()
        copy.canvas.svg = self.canvas.svg.cloneNode(True)
        copy.canvas.svg.setAttribute('width', '{0}'.format(*size))
        copy.canvas.svg.setAttribute('height', '{1}'.format(*size))
        return copy

    def convert(self, *args):
        """
        Does nothing, just for compatibility with PIL.
        :returns: An :py:class:`easy_thumbnails.VIL.Image.Image` object.
        """
        return self

    def crop(self, box=None):
        """
        Returns a rectangular region from this image. The box is a
        4-tuple defining the left, upper, right, and lower pixel
        coordinate.

        :param box: The crop rectangle, as a (left, upper, right, lower)-tuple.
        :returns: The cropped :py:class:`easy_thumbnails.VIL.Image.Image` object.
        """
        copy = Image(size=self.size)
        copy.canvas.svg = self.canvas.svg.cloneNode(True)
        if box:
            bbox = list(self.getbbox())
            current_aspect_ratio = (bbox[2] - bbox[0]) / (bbox[3] - bbox[1])
            wanted_aspect_ratio = (box[2] - box[0]) / (box[3] - box[1])
            if current_aspect_ratio > wanted_aspect_ratio:
                new_width = wanted_aspect_ratio * bbox[3]
                bbox[0] += (bbox[2] - new_width) / 2
                bbox[2] = new_width
            else:
                new_height = bbox[2] / wanted_aspect_ratio
                bbox[1] += (bbox[3] - new_height) / 2
                bbox[3] = new_height
            size = box[2] - box[0], box[3] - box[1]
            copy.canvas.svg.setAttribute('viewBox', '{0} {1} {2} {3}'.format(*bbox))
            copy.canvas.svg.setAttribute('width', '{0}'.format(*size))
            copy.canvas.svg.setAttribute('height', '{1}'.format(*size))
        return copy

    def filter(self, *args):
        """
        Does nothing, just for compatibility with PIL.
        :returns: An :py:class:`easy_thumbnails.VIL.Image.Image` object.
        """
        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def save(self, fp, format=None, **params):
        """
        Saves this image under the given filename.  If no format is
        specified, the format to use is determined from the filename
        extension, if possible.

        You can use a file object instead of a filename. In this case,
        you must always specify the format. The file object must
        implement the ``seek``, ``tell``, and ``write``
        methods, and be opened in binary mode.

        :param fp: A filename (string), pathlib.Path object or file object.
        :param format: Must be None or 'SVG'.
        :param params: Unused extra parameters.
        :returns: None
        :exception ValueError: If the output format could not be determined
           from the file name.  Use the format option to solve this.
        :exception OSError: If the file could not be written.  The file
           may have been created, and may contain partial data.
        """

        filename = ''
        open_fp = False
        if isinstance(fp, (bytes, str)):
            filename = fp
            open_fp = True
        elif isinstance(fp, Path):
            filename = str(fp)
            open_fp = True

        suffix = Path(filename).suffix.lower()
        if format != 'SVG' and suffix != '.svg':
            raise ValueError("Image format is expected to be 'SVG' and file suffix to be '.svg'")

        if open_fp:
            fp = builtins.open(filename, 'w')
        self.canvas.svg.writexml(fp)
        if open_fp:
            fp.flush()


def new(self, size, color=None):
    im = Image(size)
    if color:
        im.canvas.setFillColor(Color(*color))
    return im


def load(fp, mode='r'):
    """
    Opens and identifies the given SVG image file.

    :param fp: A filename (string), pathlib.Path object or a file object.
       The file object must implement :py:meth:`~file.read`,
       :py:meth:`~file.seek`, and :py:meth:`~file.tell` methods,
       and be opened in binary mode.
    :param mode: The mode.  If given, this argument must be "r".
    :returns: An :py:class:`easy_thumbnails.VIL.Image.Image` object.
    :exception FileNotFoundError: If the file cannot be found.
    :exception ValueError: If the ``mode`` is not "r", or if a ``StringIO``
       instance is used for ``fp``.
    """

    if mode != 'r':
        raise ValueError("bad mode {}".format(mode))
    if isinstance(fp, Path):
        filename = str(fp.resolve())
    elif isinstance(fp, (File, str)):
        filename = fp
    else:
        raise RuntimeError("Can not open file.")
    drawing = svg2rlg(filename)
    if drawing is None:
        return
        # raise ValueError("cannot decode SVG image")
    im = Image(size=(drawing.width, drawing.height))
    renderSVG.draw(drawing, im.canvas)
    return im
