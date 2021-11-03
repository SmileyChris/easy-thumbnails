def Draw(im, mode=None):
    """
    Attempting to be compatible with PIL's ImageDraw, but suitable for reportlab's SVGCanvas.

    :param im: The image to draw in.
    :param mode: ignored.
    """
    return ImageDraw(im)


class ImageDraw:
    def __init__(self, im):
        self.im = im

    def rectangle(self, xy, fill=None, outline=None, width=1):
        if fill:
            self.im.canvas.setFillColor(fill)
        if outline:
            self.im.canvas.setStrokeColor(outline)
        self.im.canvas.setLineWidth(width)
        self.im.canvas.rect(*xy)
