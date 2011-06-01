try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:
    import Image
    import ImageChops
    import ImageDraw
from easy_thumbnails import processors
from unittest import TestCase


def create_image(mode='RGB', size=(800, 600)):
    image = Image.new(mode, size)
    draw = ImageDraw.Draw(image)
    x_bit, y_bit = size[0] // 10, size[1] // 10
    draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), 'red')
    draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), 'red')
    return image


class ScaleAndCropTest(TestCase):
    def assertImagesEqual(self, im1, im2, msg=None):
        if im1.size != im2.size or \
                    ImageChops.difference(im1, im2).getbbox() is not None:
            raise self.failureException, \
                  (msg or 'The two images were not identical')

    def test_scale(self):
        image = create_image()

        scaled = processors.scale_and_crop(image, (100, 100))
        self.assertEqual(scaled.size, (100, 75))

        not_scaled = processors.scale_and_crop(image, (1000, 1000))
        self.assertEqual(not_scaled.size, (800, 600))

        upscaled = processors.scale_and_crop(image, (1000, 1000), upscale=True)
        self.assertEqual(upscaled.size, (1000, 750))

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
        expected = image.crop([0, 350, 800, 450])
        self.assertImagesEqual(y_cropped, expected)

    def test_crop_corner(self):
        image = create_image()

        tl_crop = processors.scale_and_crop(image, (100, 600), crop='0,0')
        expected = image.crop([0, 0, 100, 600])
        self.assertImagesEqual(tl_crop, expected)

        br_crop = processors.scale_and_crop(image, (100, 600), crop='-0,-0')
        expected = image.crop([700, 0, 800, 600])
        self.assertImagesEqual(br_crop, expected)

        x_offset_crop = processors.scale_and_crop(image, (150, 600),
                                                  crop='10,-10')
        expected = image.crop([15, 0, 165, 600])

        self.assertImagesEqual(x_offset_crop, expected)

        y_offset_crop = processors.scale_and_crop(image, (800, 150),
                                                  crop='10,-10')
        expected = image.crop([0, 435, 800, 585])
        self.assertImagesEqual(y_offset_crop, expected)

        only_x_crop = processors.scale_and_crop(image, (100, 600), crop='0,')
        expected = image.crop([0, 0, 100, 600])
        self.assertImagesEqual(only_x_crop, expected)

        only_y_crop = processors.scale_and_crop(image, (800, 100), crop=',0')
        expected = image.crop([0, 0, 800, 100])
        self.assertImagesEqual(only_y_crop, expected)

    def test_crop_smart(self):
        image = create_image()

        smart_crop = processors.scale_and_crop(image, (600, 600), crop='smart')
        expected = image.crop([78, 0, 678, 600])
        self.assertImagesEqual(smart_crop, expected)

    def test_crop_scale(self):
        image = create_image(size=(200, 400))

        scaled = processors.scale_and_crop(image, (100, 100), crop='scale')
        self.assertEqual(scaled.size, (100, 200))

        scaled = processors.scale_and_crop(image, (600, 600), crop='scale')
        self.assertEqual(scaled.size, (200, 400))
        scaled = processors.scale_and_crop(image, (600, 600), crop='scale',
                                           upscale=True)
        self.assertEqual(scaled.size, (600, 1200))

    def test_one_dimension_scale(self):
        image = create_image()

        scaled = processors.scale_and_crop(image, (100, 0))
        self.assertEqual(scaled.size, (100, 75))
        scaled = processors.scale_and_crop(image, (0, 100))
        self.assertEqual(scaled.size, (133, 100))

    def test_one_dimension_crop(self):
        image = create_image()

        cropped = processors.scale_and_crop(image, (100, 0), crop=True)
        self.assertEqual(cropped.size, (100, 75))
        cropped = processors.scale_and_crop(image, (0, 100), crop=True)
        self.assertEqual(cropped.size, (133, 100))

    def test_croup_rounding(self):
        image = create_image(size=(2400, 3620))

        size = (110, 1000)
        cropped = processors.scale_and_crop(image, size, crop=True)
        self.assertEqual(cropped.size, size)
