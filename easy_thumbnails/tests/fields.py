import os

from django.core.files.base import ContentFile
from django.db import models

from easy_thumbnails import test
from easy_thumbnails.fields import ThumbnailerField, ThumbnailerImageField
from easy_thumbnails.exceptions import InvalidImageFormatError


class TestModel(models.Model):
    avatar = ThumbnailerField(upload_to='avatars')
    picture = ThumbnailerImageField(upload_to='pictures',
                                    resize_source=dict(size=(10, 10)))


class ThumbnailerFieldTest(test.BaseTest):
    def setUp(self):
        super(ThumbnailerFieldTest, self).setUp()
        self.storage = test.TemporaryStorage()
        # Save a test image.
        self.create_image(self.storage, 'avatars/avatar.jpg')
        # Set the test model to use the current temporary storage.
        TestModel._meta.get_field('avatar').storage = self.storage
        TestModel._meta.get_field('avatar').thumbnail_storage = self.storage

    def tearDown(self):
        self.storage.delete_temporary_storage()
        super(ThumbnailerFieldTest, self).tearDown()

    def test_generate_thumbnail(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        thumb = instance.avatar.generate_thumbnail({'size': (300, 300)})
        self.assertEqual((thumb.width, thumb.height), (300, 225))

    def test_generate_thumbnail_type_error(self):
        text_file = ContentFile("Lorem ipsum dolor sit amet. Not an image.")
        self.storage.save('avatars/invalid.jpg', text_file)
        instance = TestModel(avatar='avatars/invalid.jpg')
        generate = lambda: instance.avatar.generate_thumbnail(
            {'size': (300, 300)})
        self.assertRaises(InvalidImageFormatError, generate)

    def test_delete(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        source_path = instance.avatar.path
        thumb_paths = (
            instance.avatar.get_thumbnail({'size': (300, 300)}).path,
            instance.avatar.get_thumbnail({'size': (200, 200)}).path,
            instance.avatar.get_thumbnail({'size': (100, 100)}).path,
        )
        self.assertTrue(os.path.exists(source_path))
        for path in thumb_paths:
            self.assertTrue(os.path.exists(path))
        instance.avatar.delete(save=False)
        self.assertFalse(os.path.exists(source_path))
        for path in thumb_paths:
            self.assertFalse(os.path.exists(path))

    def test_delete_thumbnails(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        source_path = instance.avatar.path
        thumb_paths = (
            instance.avatar.get_thumbnail({'size': (300, 300)}).path,
            instance.avatar.get_thumbnail({'size': (200, 200)}).path,
            instance.avatar.get_thumbnail({'size': (100, 100)}).path,
        )
        self.assertTrue(os.path.exists(source_path))
        for path in thumb_paths:
            self.assertTrue(os.path.exists(path))
        instance.avatar.delete_thumbnails()
        self.assertTrue(os.path.exists(source_path))
        for path in thumb_paths:
            self.assertFalse(os.path.exists(path))

    def test_get_thumbnails(self):
        instance = TestModel(avatar='avatars/avatar.jpg')
        instance.avatar.get_thumbnail({'size': (300, 300)})
        instance.avatar.get_thumbnail({'size': (200, 200)})
        self.assertEqual(len(list(instance.avatar.get_thumbnails())), 2)

    def test_saving_image_field_with_resize_source(self):
        # Ensure that saving ThumbnailerImageField with resize_source enabled
        # using instance.field.save() does not fail
        instance = TestModel(avatar='avatars/avatar.jpg')
        instance.picture.save(
            'file.jpg', ContentFile(instance.avatar.file.read()), save=False)
        self.assertEqual(instance.picture.width, 10)
