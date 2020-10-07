from unittest import TestCase
try:
    from PIL import Image, ImageCms
except ImportError:
    import Image, ImageCms

from easy_thumbnails import engine


class SaveTest(TestCase):

    def test_save_jpeg_rgba(self):
        source = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        data = engine.save_image(source, filename='test.jpg')
        img = Image.open(data)
        self.assertEqual(img.mode, 'RGB')

    def test_save_jpeg_la(self):
        source = Image.new('LA', (100, 100), (255, 0))
        data = engine.save_image(source, filename='test.jpg')
        img = Image.open(data)
        self.assertEqual(img.mode, 'L')


    def test_save_with_icc_profile(self):
        source = Image.new('RGB', (100, 100), (255, 255, 255))
        profile = ImageCms.createProfile('sRGB')
        source.save('source.jpg', icc_profile=profile.tobytes())
        source = Image.open('source.jpg')

        data = engine.save_image(source, {'keep_icc_profile': True}, filename='test.jpg')
        img = Image.open(data)

        self.assertNotEqual(img.info.get('icc_profile'), None)
