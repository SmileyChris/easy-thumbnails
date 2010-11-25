from django.db import models
from django.core.files.base import ContentFile
from easy_thumbnails.tests.utils import BaseTest, TemporaryStorage
from easy_thumbnails.fields import ThumbnailerField
try:
    from PIL import Image
except ImportError:
    import Image
from StringIO import StringIO


class TestModel(models.Model):
    avatar = ThumbnailerField(upload_to='avatars')


class ThumbnailerFieldTest(BaseTest):
    def setUp(self):
        BaseTest.setUp(self)
        self.storage = TemporaryStorage()
        # Save a test image.
        data = StringIO()
        Image.new('RGB', (800, 600)).save(data, 'JPEG')
        data.seek(0)
        image_file = ContentFile(data.read())
        self.storage.save('avatars/avatar.jpg', image_file)
        # Set the test model to use the current temporary storage.
        TestModel._meta.get_field('avatar').storage = self.storage
        TestModel._meta.get_field('avatar').thumbnail_storage = self.storage

    def tearDown(self):
        self.storage.delete_temporary_storage()
        BaseTest.tearDown(self)

    def test_generate_thumbnail(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        thumb = instance.avatar.generate_thumbnail({'size': (300, 300)})
        self.assertEqual((thumb.width, thumb.height), (300, 225))

    def test_delete(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        instance.avatar.get_thumbnail({'size': (300, 300)})
        instance.avatar.get_thumbnail({'size': (200, 200)})
        instance.avatar.get_thumbnail({'size': (100, 100)})
        self.assertEqual(len(self.storage.listdir('avatars')[1]), 4)
        instance.avatar.delete(save=False)
        self.assertEqual(len(self.storage.listdir('avatars')[1]), 0)

    def test_delete_thumbnails(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        instance.avatar.get_thumbnail({'size': (300, 300)})
        instance.avatar.get_thumbnail({'size': (200, 200)})
        instance.avatar.get_thumbnail({'size': (100, 100)})
        self.assertEqual(len(self.storage.listdir('avatars')[1]), 4)
        instance.avatar.delete_thumbnails()
        self.assertEqual(len(self.storage.listdir('avatars')[1]), 1)

    def test_get_thumbnails(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        instance.avatar.get_thumbnail({'size': (300, 300)})
        instance.avatar.get_thumbnail({'size': (200, 200)})
        self.assertEqual(len(list(instance.avatar.get_thumbnails())), 2)
