from reportlab.graphics import renderSVG
from reportlab.lib.colors import Color

from svglib.svglib import svg2rlg


class Image:
    """
    Attempting to be compatible with PIL's Image, but suitable for reportlab's SVGCanvas.
    """
    def __init__(self, size=(300, 300)):
        self.canvas = renderSVG.SVGCanvas(size=size, useClip=True)
        assert isinstance(size, (list, tuple)) and len(size) == 2, \
            "Expected `size` as tuple with two elements"
        self.size = tuple(size)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def getbbox(self):
        """
        Calculates the bounding box of the non-zero regions in the image.

        :returns: The bounding box is returned as a 4-tuple defining the
           left, upper, right, and lower pixel coordinate.
        """
        return tuple(float(b) for b in self.canvas.svg.getAttribute('viewBox').split())

    def resize(self, size, resample=None, box=None, reducing_gap=None):
        """
        :param size: The requested size in pixels, as a 2-tuple:
           (width, height).
        :param resample: Does not apply to SVG images.
        :param box: An optional 4-tuple of floats providing
           the source image region to be scaled.
           The values must be within (0, 0, width, height) rectangle.
           If omitted or None, the entire source is used.
        :param reducing_gap: Does not apply to SVG images.
        :returns: An :py:class:`easy_thumbnails.VIL.Image.Image` object.
        """
        copy = Image()
        copy.canvas.svg = self.canvas.svg.cloneNode(True)
        copy.size = tuple(size)
        return copy

    def crop(self, box=None):
        """
        Returns a rectangular region from this image. The box is a
        4-tuple defining the left, upper, right, and lower pixel
        coordinate. See :ref:`coordinate-system`.

        :param box: The crop rectangle, as a (left, upper, right, lower)-tuple.
        :returns: An :py:class:`easy_thumbnails.VIL.Image.Image` object.
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
            copy.canvas.svg.setAttribute('viewBox', '{0} {1} {2} {3}'.format(*bbox))
            copy.size = box[2] - box[0], box[3] - box[1]
        return copy


def new(self, size, color=None):
    im = Image(size)
    if color:
        im.canvas.setFillColor(Color(*color))
    return im
