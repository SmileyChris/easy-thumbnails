from unittest.mock import Mock

from django.core.files.storage import DefaultStorage, FileSystemStorage
from django.test import SimpleTestCase
from django.utils.functional import SimpleLazyObject, empty

from easy_thumbnails import utils


class StorageHashTest(SimpleTestCase):

    def test_lazy_storage_initializes_once(self):
        storage = FileSystemStorage()
        setup = Mock(return_value=storage)
        lazy_storage = SimpleLazyObject(setup)
        self.assertIs(lazy_storage._wrapped, empty)

        expected = utils.get_storage_hash(storage)
        self.assertEqual(utils.get_storage_hash(lazy_storage), expected)
        self.assertIs(lazy_storage._wrapped, storage)
        self.assertEqual(utils.get_storage_hash(lazy_storage), expected)
        setup.assert_called_once_with()

    def test_default_storage_hash_before_and_after_initialization(self):
        storage = DefaultStorage()
        self.assertIs(storage._wrapped, empty)
        before = utils.get_storage_hash(storage)
        storage.exists('nonexistent-storage-hash-test.jpg')
        self.assertEqual(before, utils.get_storage_hash(storage))
        self.assertEqual(before, utils.get_storage_hash(FileSystemStorage()))

    def test_initialized_storage_and_class_path(self):
        storage = SimpleLazyObject(FileSystemStorage)
        storage._setup()
        self.assertEqual(
            utils.get_storage_hash(storage),
            utils.get_storage_hash('django.core.files.storage.filesystem.'
                                   'FileSystemStorage'))
