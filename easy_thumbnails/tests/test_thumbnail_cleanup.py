import os
from datetime import timedelta
from django.test import override_settings
from django.core.management import call_command
from django.utils.timezone import now
from easy_thumbnails.models import Source, Thumbnail
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.tests import utils as test
from django.conf import settings


@override_settings(MEDIA_ROOT=os.path.join(settings.MEDIA_ROOT, "test_media"))
class ThumbnailCleanupTest(test.BaseTest):

    def setUp(self):
        super().setUp()
        self.storage = test.TemporaryStorage()

        # Create a source image
        filename = self.create_image(self.storage, "test.jpg")
        self.source_image_path = self.storage.open(filename).name

        # Save a test image in both storages.
        self.thumbnailer = get_thumbnailer(self.storage, filename)
        self.thumbnailer.generate_thumbnail({"size": (100, 100)})

        self.thumbnail_name = self.thumbnailer.get_thumbnail_name({"size": (100, 100)})
        self.thumbnail_path = self.thumbnailer.get_thumbnail({"size": (100, 100)}).path

        self.source = Source.objects.get(name=filename)

    def tearDown(self):
        # Clean up files
        if os.path.exists(self.source_image_path):
            os.remove(self.source_image_path)
        if os.path.exists(self.thumbnail_path):
            os.remove(self.thumbnail_path)

        # Clean up the database
        Source.objects.all().delete()
        Thumbnail.objects.all().delete()

        # Remove test media directory if empty
        if os.path.exists(settings.MEDIA_ROOT) and not os.listdir(settings.MEDIA_ROOT):
            os.rmdir(settings.MEDIA_ROOT)

    def test_cleanup_command(self):
        print(self.source_image_path)
        self.assertTrue(os.path.exists(self.source_image_path))
        self.assertTrue(os.path.exists(self.thumbnail_path))

        # Delete the source image to simulate a missing source image
        os.remove(self.source_image_path)
        self.assertFalse(os.path.exists(self.source_image_path))

        # Run the thumbnail cleanup command
        call_command("thumbnail_cleanup", verbosity=2)

        # Verify the thumbnail has been deleted
        self.assertFalse(os.path.exists(self.thumbnail_path))

        # Verify the source reference has been deleted
        with self.assertRaises(Source.DoesNotExist):
            Source.objects.get(id=self.source.id)

    def test_cleanup_dry_run(self):
        self.assertTrue(os.path.exists(self.source_image_path))
        self.assertTrue(os.path.exists(self.thumbnail_path))

        # Delete the source image to simulate a missing source image
        os.remove(self.source_image_path)
        self.assertFalse(os.path.exists(self.source_image_path))

        # Run the thumbnail cleanup command in dry run mode
        call_command("thumbnail_cleanup", dry_run=True, verbosity=2)

        # Verify the thumbnail has not been deleted
        self.assertTrue(os.path.exists(self.thumbnail_path))

        # Verify the source reference has not been deleted
        self.assertIsNotNone(Source.objects.get(id=self.source.id))

    def test_cleanup_last_n_days(self):
        old_time = now() - timedelta(days=10)
        self.source.modified = old_time
        self.source.save()

        self.assertTrue(os.path.exists(self.source_image_path))
        self.assertTrue(os.path.exists(self.thumbnail_path))

        # Delete the source image to simulate a missing source image
        os.remove(self.source_image_path)
        self.assertFalse(os.path.exists(self.source_image_path))

        # Run the thumbnail cleanup command with last_n_days parameter
        call_command("thumbnail_cleanup", last_n_days=5, verbosity=2)

        # Verify the thumbnail has not been deleted
        self.assertTrue(os.path.exists(self.thumbnail_path))

        # Verify the source reference has not been deleted
        self.assertIsNotNone(Source.objects.get(id=self.source.id))

        # Run the thumbnail cleanup command with last_n_days parameter that includes the source
        call_command("thumbnail_cleanup", last_n_days=15, verbosity=2)

        # Verify the thumbnail has been deleted
        self.assertFalse(os.path.exists(self.thumbnail_path))

        # Verify the source reference has been deleted
        with self.assertRaises(Source.DoesNotExist):
            Source.objects.get(id=self.source.id)

    def test_source_storage_hash_not_found(self):
        self.assertTrue(os.path.exists(self.source_image_path))
        self.assertTrue(os.path.exists(self.thumbnail_path))

        # Change the source's storage_hash to simulate an unknown storage hash
        self.source.storage_hash = "unknown_storage_hash"
        self.source.save()

        # Run the thumbnail cleanup command
        call_command("thumbnail_cleanup", verbosity=2)

        # Verify the thumbnail and source still exist
        self.assertTrue(os.path.exists(self.thumbnail_path))
        self.assertIsNotNone(Source.objects.get(id=self.source.id))
