from unittest import TestCase
from PIL import Image

from easy_thumbnails import engine


class SaveTest(TestCase):

    def test_save_jpeg_rgba(self):
        source = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        data = engine.save_image(source, filename='test.jpg')
        with Image.open(data) as img:
            self.assertEqual(img.mode, 'RGB')

    def test_save_jpeg_la(self):
        source = Image.new('LA', (100, 100), (255, 0))
        data = engine.save_image(source, filename='test.jpg')
        with Image.open(data) as img:
            self.assertEqual(img.mode, 'L')
