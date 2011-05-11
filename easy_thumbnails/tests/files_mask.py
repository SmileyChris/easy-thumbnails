try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image, ImageDraw
except ImportError:
    import Image
    import ImageDraw

from easy_thumbnails import files_mask
from unittest import TestCase

class MaskFile(TestCase):
    def setUp(self):
        file = StringIO()
        Image.new('RGB', (100, 100)).save(file, 'PNG')
        file.seek(0)
        self.mask = files_mask.MaskFile(file, 'some/path/name.png')

    def test_str(self):
        self.assertEqual(str(self.mask), 'name')

    def test_unicode(self):
        self.assertEqual(unicode(self.mask), u'name')

    def test_get_image(self):
        self.assertFalse(self.mask.image is None)

class Mask(TestCase):
    def test_get_path(self):
        name = 'somename'

        class MaskMock(files_mask.Mask):
            def open(self):
                return None

        mask_mock = MaskMock(name)
        mask_mock.STATIC_ROOT = '/test/path/'

        self.assertEqual(mask_mock.get_path(name), u'/test/path/somename.png')
