from easy_thumbnails.VIL import Image, ImageChops, ImageDraw
from easy_thumbnails import processors
from reportlab.lib.colors import Color
from unittest import TestCase


def create_image(mode='RGB', size=(800, 600)):
    image = Image.new(mode, size, (255, 255, 255))
    draw = ImageDraw.Draw(image)
    x_bit, y_bit = size[0] // 10, size[1] // 10
    draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), Color(red=255))
    draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), Color(red=255))
    return image


class ScaleAndCropTest(TestCase):
    def assertImagesEqual(self, im1, im2, msg=None):
        if im1.size != im2.size or (
                ImageChops.difference(im1, im2).getbbox() is not None):
            raise self.failureException(
                msg or 'The two images were not identical')

    def test_scale(self):
        image = create_image()

        scaled = processors.scale_and_crop(image, (100, 100))
        self.assertEqual(scaled.size, (800, 600))

        not_scaled = processors.scale_and_crop(image, (1000, 1000))
        self.assertEqual(not_scaled.size, (800, 600))

        upscaled = processors.scale_and_crop(image, (1000, 1000), upscale=True)
        self.assertEqual(upscaled.size, (800, 600))

    def test_crop(self):
        image = create_image()

        both_cropped = processors.scale_and_crop(image, (100, 100), crop=True)
        self.assertEqual(both_cropped.size, (100, 100))

        not_cropped = processors.scale_and_crop(image, (1000, 1000), crop=True)
        self.assertEqual(not_cropped.size, (800, 600))

        x_cropped = processors.scale_and_crop(image, (600, 600), crop=True)
        expected = image.crop([100, 0, 700, 600])
        self.assertImagesEqual(x_cropped, expected)

        y_cropped = processors.scale_and_crop(image, (1000, 100), crop=True)
        expected = image.crop([0, 250, 800, 350])
        self.assertImagesEqual(y_cropped, expected)
