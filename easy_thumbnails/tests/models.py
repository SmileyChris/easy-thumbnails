"""Tests for the models module.
"""

from easy_thumbnails import utils, test
from easy_thumbnails.models import Thumbnail, Source


class FileManagerTest(test.BaseTest):
    """Test for FileManager"""

    def setUp(self):
        super(FileManagerTest, self).setUp()

        self.storage = test.TemporaryStorage()
        self.storage_hash = utils.get_storage_hash(self.storage)
        self.source = Source.objects.create(
                name='Test source',
                storage_hash=self.storage_hash)

        # Generate a test image, save it.
        self.filename = self.create_image(self.storage, 'test.jpg')

    def tearDown(self):
        self.storage.delete_temporary_storage()
        super(FileManagerTest, self).tearDown()

    def test_create_file(self):
        """Create a new Thumbnail in the database"""
        img = Thumbnail.objects.get_file(
                self.storage,
                self.filename,
                create=True,
                source=self.source)

        self.assertEquals(img.name, self.filename)

    def test_get_file(self):
        """Fetch an existing thumb from database"""
        created = Thumbnail.objects.create(
                storage_hash=self.storage_hash,
                name=self.filename,
                source=self.source)

        fetched = Thumbnail.objects.get_file(
                self.storage,
                self.filename,
                create=False)

        self.assertTrue(fetched)
        self.assertEquals(created, fetched)

    def test_get_file_check_cache(self):
        """Fetch a thumb that is in the storage but not in the database"""

        # It's not in the database yet
        try:
            Thumbnail.objects.get(name=self.filename)
            self.fail('Thumb should not exist yet')
        except Thumbnail.DoesNotExist:
            pass

        Thumbnail.objects.get_file(
                self.storage,
                self.filename,
                source=self.source,
                check_cache_miss=True)

        # Now it is
        try:
            Thumbnail.objects.get(name=self.filename)
        except Thumbnail.DoesNotExist:
            self.fail('Thumb should exist now')
