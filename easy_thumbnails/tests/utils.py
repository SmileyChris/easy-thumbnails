from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.test import TestCase
from easy_thumbnails import defaults
import shutil
import tempfile


class TemporaryStorage(FileSystemStorage):
    def __init__(self, location=None, *args, **kwargs):
        if location is None:
            location = tempfile.mkdtemp()
            self.temporary_location = location
        super(TemporaryStorage, self).__init__(location=location, *args,
                                               **kwargs)

    def delete_temporary_storage(self):
        temporary_location = getattr(self, 'temporary_location', None)
        if temporary_location:
            shutil.rmtree(temporary_location)


class FakeRemoteStorage(TemporaryStorage):
    def path(self, *args, **kwargs):
        raise NotImplementedError


class BaseTest(TestCase):
    restore_settings = ['THUMBNAIL_%s' % key for key in dir(defaults)
                        if key.isupper()]

    def setUp(self):
        self._remembered_settings = {}
        for setting in self.restore_settings:
            if hasattr(settings, setting):
                self._remembered_settings[setting] = getattr(settings, setting)
                delattr(settings._wrapped, setting)

    def tearDown(self):
        for setting in self.restore_settings:
            self.restore_setting(setting)

    def restore_setting(self, setting):
        if setting in self._remembered_settings:
            value = self._remembered_settings.pop(setting)
            setattr(settings, setting, value)
        elif hasattr(settings, setting):
            delattr(settings._wrapped, setting)
