from StringIO import StringIO
try:
    from PIL import Image, ImageChops, ImageDraw
except ImportError:
    import Image
    import ImageChops
    import ImageDraw
from easy_thumbnails import processors
from unittest import TestCase

EXIF_REFERENCE = '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAAAQAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABgAAAMBAQAAAAAAAAAAAAAAAAAICgkL/8QAPhAAAAIGBgQGEwAAAAAAAAAABxYABAUGFRcICRMUGCUDChkaIyc3ZoinJDQ1OUVHSVdYZ2imqLjI1tfm5//aAAgBAQAAPwC/hBBBIA9tpWdekz1M0ffxQlftVwNon0jKCYGDKMrzHESXxmaY3jgrvO9ES8MQguqx8ndVksNgqdzYLDZah2Ay1W8XW9LVuu6dYWNMU5xtE8HJXS4eYuGM7RnJXea98hBRh3d5ktS73eKL3atha2/D2tlobNAMbVJ3zm+5gffaiKruy/tsfDd/e0QAbdYb2CInvNVN4QsVuFKC8fs/5Fn2ejvMmkpyVyUGIrFacRL5R3jjZcMeUReBMt/6sus03i6dnEng7wdy38ZGIOYuIM+8wgQKJRkhznj5n8CwXNtVNmX67Orf99TVROQLrR3f16c3Rm+Tyj6m/wBqMflRehN9XCX+J//Z'
EXIF_ORIENTATION = {
    2: '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAAAgAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABgAAAMBAQAAAAAAAAAAAAAAAAAJCggL/8QAQRAAAAEKAQQJFQAAAAAAAAAAFgAEBQYHCBQVFxgDCQoTGQIaJCUmNkaIpxIjJzU3OUlXWGVmZ2imqLjI1tfm5//aAAgBAQAAPwC/ggggkA3tPO+M33MZ99qE391xd1naMwlRlyXJJzlZEyJpkkoJHo+Jl64rCijPcaKNDEwwdCYGJrgdYNcLSaLS4vV42zxMTZqAy5z7TzrnVrtuLTadVFrYMuBjPlunARpGHuPaqLPL5eJ052qgYuO3dEwxnDoB12mU68pnoZd9/FBVUasv12dG/wC+kgF9rOaNTo8603JxWT3F26AzsyXI0iGNXWfKo3bueUEaeHg9U8LceU5NpHPN7ZlJ0eOyvNba6G3AmwqwoN8pLpKrXST/AMwO6AUC26emInGPJ4Pb+aq2sv7bHw3f3sqqC5AudHd/Xfm5s3yeO+k/7MY/Ci8yb6uCv8L/2Q==',
    3: '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAAAwAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABgAAAMBAQAAAAAAAAAAAAAAAAAICgkL/8QAQxAAAAEIAwcODwAAAAAAAAAAFQAFBgcIFBYXCRMZAwQKGCUmJxojJCg0NTY3ODlER4inSVdYZWZnaKaouMjW1+bn/9oACAEBAAA/AL+C5AuFHc+u3N2Zvk8Z9Lf7AY/Ci9ib6uCv8LAHHaad8ZvuYr77UIsS6MWkX25LZLM04mkVxcY6x5zNBK9iKX2ixEM0FWLXQdAzQEIGg6LmLISLmt/CxQ6Pp5v04nG+0AbnUkrCgRldZNozipY1sbT9y0kK9I9kXCMq+UmdlxQtC04lj8C4cG4jzjFwgxBaAW2lJ15TPcyz7+KCqosy/XZ3b/vpP+pJWUnFYIyrgbiOHBrLIaEPgukJ2P29z+dHd3FHXd13raiv1qtqbmgFJpRl2i8k9NknZOzI6t5hRFMKAvT1BwgIgfzo/inQnLZeVepl/bY+G7+9lVQQQQX/2Q==',
    4: '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAABAAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABkAAAIDAQAAAAAAAAAAAAAAAAAJBwgKC//EAD4QAAADBQQEBBcAAAAAAAAAAAcVFgAFBggUCRcYJgQKGTc2OYinExojJCU1Q0ZJV1hkZWdopqi4yNbX5uf/2gAIAQEAAD8A38NyBdaO49eebkzfJ5L6z/tRj8KLyJvq4bf42APbaWnXlM8zMvv4oZv8rlkFZ2WroEwNP5P5Lzf3NqPamvYFi9kcgtVd1sYxCC8CZEBcTA6DRxEQaBzBsNZag1zmZOcvkwf7wer106f8EssVjpxcQZYdMRe+TOYgi6sbot3m/aKxPTyevPjngsRmx52cMi1zl5jamd8ZvuYH32o1Vell/bY+G7+9s/6SWWXB1LEGUuK2vFu6Weck2kThXCDFcd8Hj+Jy8vU5V2806roa7rapo9HJmpZcRiJzsjkcpO9tQmKhIPT7jo6Mj86qKruHQOrVV2Zfrs5t/wB9ZqjDDDf/2Q==',
    5: '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAABQAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABgAAAMBAQAAAAAAAAAAAAAAAAgJCgAL/8QAPhAAAAIGBwIFFQAAAAAAAAAABxYABQYUFRcDBAgJExglCho4R2aHqBkjJCYnNDU2OUVIWGmGiLe4xsfY6P/aAAgBAQAAPwC/hIA77TynVpnmZ+n0KEapsy/psfDd+e0qoTIAA23XFhO0YJ7TDKMoGHESWxgpjaOZoxM9ES8zypZVT6OyogqNQ1NzUKjVdQ7AVdVeHV6rWPXaesVimlX2hsbRPuEcoXUm2mypZrZ/z90Vnh0Psi5KSr4SapGIrFacQj+JZcjZj7Y4vCFFC5rN6Ov1/Xm6M1jz9fU6/SAANtueTgntMHErjGXILrJ2hD5F2eVK+8HFFaO7vFHXv6nxcDH61i4NGla80uy94ukn3bMneTuZHFvmDmLmDIXL0ECiUZIcp4+Z/MsF1ZVe4x+1F6E39cJf4iAbbXCdE33M+XzKIVV2Xx2c2/36jVE//9k=',
    6: '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAABgAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABkAAAIDAQAAAAAAAAAAAAAAAAkKAAcIC//EAEAQAAAACgQICA8AAAAAAAAAAAAEBQYHCBUWFxgDCRMUAgoaJCUmNkYSGSM1NziHqDlHSFhlZmmGiLe4xsfY6P/aAAgBAQAAPwB/gAArtdZ1JvuZ8vjUDVVWX47Ozf79AqgQKAPdVxBKRjnKZ5HkYzZOQs3JpFJ5jxJ95Z5PFCUJ5mSjhERChsRARFaDkBWitLK1peHTYdJSYalmM0LtLO1Okk/FxJNl0mLmRjJqYj5Lr4wigJDzp2NRJ7vO9E8+dlmG1m5pxpM0js9VfKjq9fz5u7Mp5+vodfoAArtV50nSzqTVcZXYiw6czXKNroth7kfGofez0IznZ7Pedlc+D17uN+za83MXFWs0rLlXTk67SFSFPJu3NJFaaRgen1dHFcWXT1xed8d3ne05lXIY/ai9yb+uAf8AAQDrtPCdLM9jP0+ooAqmLL+Wx8N357BqgP/Z',
    7: '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAABwAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABkAAAIDAQAAAAAAAAAAAAAAAAkKAAcIC//EAEAQAAABCQEIDQ0AAAAAAAAAABUABQYHCAkUFhcTBBgZGiUnN0cDCiMkJik0NTg5RIeoSFhlZmmGiLe4xsfY6P/aAAgBAQAAPwB/ggAttdJ1ZvuZ8vkULVTsvXZ3b/fpFULkC40c/X8+bwzMefr6T/jkvjF3YrMzZLZOeJpFcVZqjrH0ezFT5oJa6rEQ4IKskdAzQEIGg6LmLISLmuPCxQ6Rp5u04nG6zUqyUkrBTg3ThGZcmMNGctJCd4wIjw7n47HSHhxS7uS2Frb7va2Ww2dqkgHiMftRfBN/XBb/AFJNz4BFWCMum6XX1t6kNZ/Z2oXPtdEhOzSmiuUVxStK1YpL0jpGNy5MeSBcCNZqXZbzTCL1szJ0do7TfWRUKYqhT76hIOEBEj+lI8U7FBb7KoUJAN9p1nTTPcz9PqqCKptZfy2Phu/PZNUF/9k=',
    8: '/9j/4AAQSkZJRgABAQEASABIAAD/4QAiRXhpZgAASUkqAAgAAAABABIBAwABAAAACAAAAAAAAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH//gAdQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWMA/8AACwgAHgAeAQERAP/EABgAAAMBAQAAAAAAAAAAAAAAAAgJCgAL/8QAPxAAAAMGAQQJFQAAAAAAAAAABxUWAAUGCBQXCQQYGiYKEyMnNjc4h6gkJSk1OUNGR0hYZGVphoi3uMbH2Oj/2gAIAQEAAD8Av4aAPG07p1MzzM/T6FDNU2Mv5bHw3fntqqG5AulHY6/nzdGaTz9fWt9wgpXAJxXcOyXmfyfyBr9zaj3dm7AsKaMQtVdrRyEwF4E1EBeIQ6DRxEQaBzBsNatQa5zMnOXyYP8AeD1euXPTllkllik6W2biGVuriptZa5iDFxwkT9PcO4ricvL1O/O1VDV13V1TTZHTlU0Aegx+1F6E39cM/wCkl7DpLEGWHFyi83RZ78nFEsbuiDFY7cXm+enk9c9LcOX4bEZ51tMid3tUllmazjFtqSjkcm/CRQmKhP8A1A46OjI/Sqiq7xtG7FU2ZAM7XKdE33M+X0KMVWGX47Obf79Zqjf/2Q==',
}


def create_image(mode='RGB', size=(800, 600)):
    image = Image.new(mode, size)
    draw = ImageDraw.Draw(image)
    x_bit, y_bit = size[0] // 10, size[1] // 10
    draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), 'red')
    draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), 'red')
    return image


def image_from_b64(data):
    return Image.open(StringIO(data.decode('base64')))


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


class ColorspaceTest(TestCase):

    def test_standard(self):
        image = Image.new('RGB', (800, 600))
        processed = processors.colorspace(image)
        self.assertEqual(processed.mode, 'RGB')

        image = Image.new('L', (800, 600))
        processed = processors.colorspace(image)
        self.assertEqual(processed.mode, 'L')

    def test_transparent(self):
        image = Image.new('RGBA', (800, 600))
        processed = processors.colorspace(image)
        self.assertEqual(processed.mode, 'RGBA')

        image = Image.new('LA', (800, 600))
        processed = processors.colorspace(image)
        self.assertEqual(processed.mode, 'RGBA')

    def test_replace_alpha(self):
        image = Image.new('RGBA', (800, 600))
        processed = processors.colorspace(image, replace_alpha='#fff')
        self.assertEqual(processed.mode, 'RGB')

        image = Image.new('LA', (800, 600))
        processed = processors.colorspace(image, replace_alpha='#fff')
        self.assertEqual(processed.mode, 'RGB')

    def test_bw(self):
        image = Image.new('RGB', (800, 600))
        processed = processors.colorspace(image, bw=True)
        self.assertEqual(processed.mode, 'L')

        image = Image.new('RGBA', (800, 600))
        processed = processors.colorspace(image, bw=True)
        self.assertEqual(processed.mode, 'LA')

        image = Image.new('L', (800, 600))
        processed = processors.colorspace(image, bw=True)
        self.assertEqual(processed.mode, 'L')

        image = Image.new('LA', (800, 600))
        processed = processors.colorspace(image, bw=True)
        self.assertEqual(processed.mode, 'LA')


class ExifOrientationTest(TestCase):

    def setUp(self):
        self.reference = image_from_b64(EXIF_REFERENCE)

    def near_identical(self, im1, im2):
        diff = ImageChops.difference(im1, im2).histogram()
        for color in diff[2:]:
            if color:
                return False
        return True

    def test_change_orientation(self):
        for exif_orientation, data in EXIF_ORIENTATION.iteritems():
            im = image_from_b64(data)
            self.assertEqual(exif_orientation, im._getexif().get(0x0112))
            self.assertFalse(self.near_identical(self.reference, im))

            im = processors.exif_orientation(im)
            self.assertTrue(self.near_identical(self.reference, im),
               'EXIF orientation %s did not match reference image' %
                   exif_orientation)


if __name__ == '__main__':
    ref = image_from_b64(EXIF_REFERENCE)
    bad = image_from_b64(EXIF_ORIENTATION[2])

    #ref.show()
    #processors.exif_orientation(bad).show()

    new = processors.exif_orientation(bad)
    s = StringIO()
    new.save(s, 'PNG')
    import base64
    s.seek(0)
    #print base64.b64encode(s.read())
    #print EXIF_REFERENCE
    print ImageChops.difference(ref, new).histogram()
    #import ipdb; ipdb.set_trace()
