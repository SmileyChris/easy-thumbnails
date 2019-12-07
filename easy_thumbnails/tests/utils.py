import shutil
import tempfile
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.test import TestCase
from PIL import Image
from easy_thumbnails.conf import settings


class TemporaryStorage(FileSystemStorage):
    """
    A storage class useful for tests that uses a temporary location to store
    all files and provides a method to remove this location when it is finished
    with.
    """

    def __init__(self, location=None, *args, **kwargs):
        """
        Create the temporary location.
        """
        if location is None:
            location = tempfile.mkdtemp()
            self.temporary_location = location
        super().__init__(location=location, *args,
                                               **kwargs)

    def delete_temporary_storage(self):
        """
        Delete the temporary directory created during initialisation.
        This storage class should not be used again after this method is
        called.
        """
        temporary_location = getattr(self, 'temporary_location', None)
        if temporary_location:
            shutil.rmtree(temporary_location)


class FakeRemoteStorage(TemporaryStorage):
    """
    A temporary storage class that acts similar to remote storage.

    It's not thread safe.
    """
    remote_mode = False

    def path(self, *args, **kwargs):
        """
        Raise ``NotImplementedError``, since this is the way that
        easy-thumbnails determines if a storage is remote.
        """
        if self.remote_mode:
            raise NotImplementedError
        return super().path(*args, **kwargs)

    def exists(self, *args, **kwargs):
        original_remote_mode = self.remote_mode
        self.remote_mode = False
        try:
            return super().exists(*args, **kwargs)
        finally:
            self.remote_mode = original_remote_mode

    def save(self, *args, **kwargs):
        self.remote_mode = False
        try:
            return super().save(*args, **kwargs)
        finally:
            self.remote_mode = True

    def open(self, *args, **kwargs):
        self.remote_mode = False
        try:
            return super().open(*args, **kwargs)
        finally:
            self.remote_mode = True

    def delete(self, *args, **kwargs):
        self.remote_mode = False
        try:
            return super().delete(*args, **kwargs)
        finally:
            self.remote_mode = True


class BaseTest(TestCase):
    """
    Remove any customised THUMBNAIL_* settings in a project's ``settings``
    configuration module before running the tests to ensure there is a
    consistent test environment.
    """

    def setUp(self):
        """
        Isolate all settings.
        """
        output = super().setUp()
        settings.isolated = True
        return output

    def tearDown(self):
        """
        Restore settings to their original state.
        """
        settings.isolated = False
        settings.revert()
        return super().tearDown()

    def create_image(self, storage, filename, size=(800, 600),
                     image_mode='RGB', image_format='JPEG'):
        """
        Generate a test image, returning the filename that it was saved as.

        If ``storage`` is ``None``, the BytesIO containing the image data
        will be passed instead.
        """
        data = BytesIO()
        Image.new(image_mode, size).save(data, image_format)
        data.seek(0)
        if not storage:
            return data
        image_file = ContentFile(data.read())
        return storage.save(filename, image_file)
