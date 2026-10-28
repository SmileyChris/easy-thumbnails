import os
import pickle

from django import VERSION as DJANGO_VERSION
from django.core.files.base import ContentFile

from easy_thumbnails.tests import utils, models
from easy_thumbnails.tests.test_aliases import BaseTest as AliasBaseTest
from easy_thumbnails.engine import NoSourceGenerator
from easy_thumbnails.exceptions import (
    InvalidImageFormatError, EasyThumbnailsError)


class ThumbnailerFieldTest(AliasBaseTest):
    def setUp(self):
        super().setUp()
        self.storage = utils.TemporaryStorage()
        # Save a test image.
        self.create_image(self.storage, 'avatars/avatar.jpg')
        # Set the test model to use the current temporary storage.
        for name in ('avatar', 'picture'):
            field = models.TestModel._meta.get_field(name)
            field.storage = self.storage
            field.thumbnail_storage = self.storage

    def tearDown(self):
        self.storage.delete_temporary_storage()
        super().tearDown()

    def test_generate_thumbnail(self):
        instance = models.TestModel(avatar='avatars/avatar.jpg')
        thumb = instance.avatar.generate_thumbnail({'size': (300, 300)})
        self.assertEqual((thumb.width, thumb.height), (300, 225))

    def test_generate_thumbnail_bad_image(self):
        text_file = ContentFile("Lorem ipsum dolor sit amet. Not an image.")
        self.storage.save('avatars/invalid.jpg', text_file)
        instance = models.TestModel(avatar='avatars/invalid.jpg')
        generate = lambda: instance.avatar.generate_thumbnail(
            {'size': (300, 300)})
        self.assertRaises(NoSourceGenerator, generate)

    def test_generate_thumbnail_alias_bad_image(self):
        text_file = ContentFile("Lorem ipsum dolor sit amet. Not an image.")
        self.storage.save('avatars/invalid.jpg', text_file)
        instance = models.TestModel(avatar='avatars/invalid.jpg')
        generate = lambda: instance.avatar['small']
        self.assertRaises(InvalidImageFormatError, generate)

    def test_generate_thumbnail_alias_0x0_size(self):
        instance = models.TestModel(avatar='avatars/avatar.jpg')
        self.assertRaises(
            EasyThumbnailsError,
            instance.avatar.generate_thumbnail, {'size': (0, 0)})

    def test_delete(self):
        instance = models.TestModel(avatar='avatars/avatar.jpg')
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
        instance = models.TestModel(avatar='avatars/avatar.jpg')
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
        instance = models.TestModel(avatar='avatars/avatar.jpg')
        instance.avatar.get_thumbnail({'size': (300, 300)})
        instance.avatar.get_thumbnail({'size': (200, 200)})
        self.assertEqual(len(list(instance.avatar.get_thumbnails())), 2)

    def test_serialization(self):
        instance = models.TestModel(avatar='avatars/avatar.jpg')
        self.assertEqual('/media/avatars/avatar.jpg.100x100_q85.jpg', instance.avatar['small'].url)
        new_instance = pickle.loads(pickle.dumps(instance))
        self.assertEqual('/media/avatars/avatar.jpg.100x100_q85.jpg', new_instance.avatar['small'].url)

    def _read_filefield(self, field):
        if DJANGO_VERSION < (2, 0):
            try:
                return field.file.read()
            finally:
                field.file.close()

        with field.open('rb') as fd:
            return fd.read()

    def test_saving_image_field_with_resize_source(self):
        # Ensure that saving ThumbnailerImageField with resize_source enabled
        # using instance.field.save() does not fail
        instance = models.TestModel(avatar='avatars/avatar.jpg')
        instance.picture.save(
            'file.jpg', ContentFile(self._read_filefield(instance.avatar)), save=False)

        self.assertEqual(instance.picture.width, 10)

    def test_saving_image_field_with_resize_source_different_ext(self):
        instance = models.TestModel(avatar='avatars/avatar.jpg')
        instance.picture.save(
            'file.gif', ContentFile(self._read_filefield(instance.avatar)), save=False)

        self.assertEqual(instance.picture.name, 'pictures/file.jpg')


class ResizedDimensionTest(utils.BaseTest):
    def setUp(self):
        super().setUp()
        self.storage = utils.TemporaryStorage()
        field = models.DimensionModel._meta.get_field('picture')
        self.old_storage = field.storage
        self.old_thumbnail_storage = field.thumbnail_storage
        field.storage = self.storage
        field.thumbnail_storage = self.storage

    def tearDown(self):
        field = models.DimensionModel._meta.get_field('picture')
        field.storage = self.old_storage
        field.thumbnail_storage = self.old_thumbnail_storage
        self.storage.delete_temporary_storage()
        super().tearDown()

    def image(self, name='original.jpg', size=(400, 200)):
        data = self.create_image(None, name, size=size)
        return ContentFile(data.read(), name=name)

    def assert_dimensions(self, instance, expected):
        saved = type(instance).objects.get(pk=instance.pk)
        self.assertEqual((saved.width, saved.height), expected)
        self.assertEqual((saved.picture.width, saved.picture.height), expected)
        self.assertEqual((instance.width, instance.height), expected)

    def test_model_save_persists_resized_dimensions(self):
        instance = models.DimensionModel(picture=self.image())
        instance.save()
        self.assert_dimensions(instance, (100, 50))

    def test_replacing_image_persists_new_dimensions(self):
        instance = models.DimensionModel.objects.create(picture=self.image())
        instance.picture = self.image('replacement.jpg', size=(200, 400))
        instance.save()
        self.assert_dimensions(instance, (50, 100))

    def test_explicit_image_save_without_model_save(self):
        instance = models.DimensionModel()
        instance.picture.save('explicit.jpg', self.image(), save=False)
        instance.save()
        self.assert_dimensions(instance, (100, 50))

    def test_partial_save_with_image_and_dimensions(self):
        instance = models.DimensionModel.objects.create(picture=self.image())
        instance.picture = self.image('replacement.jpg', size=(200, 400))
        instance.save(update_fields={'picture', 'width', 'height'})
        self.assert_dimensions(instance, (50, 100))

    def test_partial_save_without_image_does_not_write_pending_file(self):
        instance = models.DimensionModel.objects.create(picture=self.image())
        original = instance.picture.name
        instance.picture = self.image('pending.jpg', size=(200, 400))
        instance.label = 'updated'
        instance.save(update_fields={'label'})
        saved = models.DimensionModel.objects.get(pk=instance.pk)
        self.assertEqual(saved.picture.name, original)
        self.assertEqual((saved.width, saved.height), (100, 50))
        self.assertFalse(instance.picture._committed)
        self.assertFalse(self.storage.exists('pictures/pending.jpg'))

    def test_inherited_model_persists_resized_dimensions(self):
        instance = models.DimensionChild(picture=self.image())
        instance.save()
        self.assert_dimensions(instance, (100, 50))

    def test_raw_save_does_not_resize_pending_image(self):
        instance = models.DimensionModel(picture=self.image())
        instance.save_base(raw=True)
        self.assertFalse(instance.picture._committed)
        self.assertFalse(self.storage.exists('pictures/original.jpg'))
        saved = models.DimensionModel.objects.get(pk=instance.pk)
        self.assertEqual((saved.width, saved.height), (400, 200))
