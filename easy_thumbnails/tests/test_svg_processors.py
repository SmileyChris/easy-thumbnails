import unittest
from easy_thumbnails import processors, VIL


def create_image(mode='RGB', size=(800, 600)):
    from easy_thumbnails.VIL import Image, ImageDraw
    from reportlab.lib.colors import Color

    image = Image.new(mode, size, (255, 255, 255))
    draw = ImageDraw.Draw(image)
    x_bit, y_bit = size[0] // 10, size[1] // 10
    draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), Color(red=255))
    draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), Color(red=255))
    return image


@unittest.skipUnless(VIL.is_available(), "SVG support not available")
class ScaleAndCropTest(unittest.TestCase):
    def test_scale(self):
        image = create_image()

        scaled = processors.scale_and_crop(image, (100, 100))
        self.assertEqual(scaled.size, (100, 75))
        self.assertEqual(scaled.getbbox(), (0, 0, 800, 600))

        not_scaled = processors.scale_and_crop(image, (1000, 1000))
        self.assertEqual(not_scaled.size, (800, 600))
        self.assertEqual(not_scaled.getbbox(), (0, 0, 800, 600))

        upscaled = processors.scale_and_crop(image, (1000, 1000), upscale=True)
        self.assertEqual(upscaled.size, (1000, 750))
        self.assertEqual(upscaled.getbbox(), (0, 0, 800, 600))

        empty = processors.scale_and_crop(create_image(size=(0, 0)), (1000, 1000))
        self.assertEqual(empty.size, (0, 0))
        self.assertEqual(empty.getbbox(), (0, 0, 0, 0))

    def test_crop(self):
        image = create_image()

        x_cropped = processors.scale_and_crop(image, (100, 100), crop=True)
        self.assertEqual(x_cropped.size, (100, 100))
        self.assertEqual(x_cropped.getbbox(), (100, 0, 600, 600))

        not_cropped = processors.scale_and_crop(image, (1000, 1000), crop=True)
        self.assertEqual(not_cropped.size, (800, 600))
        self.assertEqual(not_cropped.getbbox(), (0, 0, 800, 600))

        y_cropped = processors.scale_and_crop(image, (400, 200), crop=True)
        self.assertEqual(y_cropped.size, (400, 200))
        self.assertEqual(y_cropped.getbbox(), (0, 100, 800, 400))

        upscaled = processors.scale_and_crop(image, (1000, 1000), crop=True, upscale=True)
        self.assertEqual(upscaled.size, (1000, 1000))
        self.assertEqual(upscaled.getbbox(), (100, 0, 600, 600))

        empty = processors.scale_and_crop(
            create_image(size=(0, 0)), (1000, 1000), crop=True
        )
        self.assertEqual(empty.size, (0, 0))
        self.assertEqual(empty.getbbox(), (0, 0, 0, 0))
