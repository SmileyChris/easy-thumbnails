from django.db import models
from django.core.files.base import ContentFile
from easy_thumbnails.tests.utils import BaseTest, TemporaryStorage
from easy_thumbnails.fields import ThumbnailerField
from PIL import Image
from StringIO import StringIO


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
        # Create a test model which uses the temporary storage.
        class TestModel(models.Model):
            avatar = ThumbnailerField(upload_to='avatars',
                                      storage=self.storage)
        self.model = TestModel

    def tearDown(self):
        BaseTest.tearDown(self)
        self.storage.delete_temporary_storage()

    def test_generate_thumbnail(self):
        instance = self.model(avatar='avatars/avatar.jpg')
        thumb = instance.avatar.generate_thumbnail({'size': (300, 300)})
        self.assertEqual((thumb.width, thumb.height), (300, 225))
