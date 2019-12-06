from django.core.files import storage as django_storage
from django.db.models import FileField
from django.db.models.signals import post_save, pre_save

from easy_thumbnails import files, signal_handlers, signals, storage
from easy_thumbnails.alias import aliases
from easy_thumbnails.conf import settings
from easy_thumbnails.tests import models, utils


class BaseTest(utils.BaseTest):
    create_file = False

    def setUp(self):
        super().setUp()
        settings.THUMBNAIL_ALIASES = {
            '': {
                'large': {'size': (500, 500)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            },
            'easy_thumbnails_tests.Profile': {
                'large': {'size': (200, 200)},
                'banner': {'size': (600, 80), 'crop': True},
            },
            'easy_thumbnails_tests.Profile.avatar': {
                'avatar': {'size': (80, 80), 'crop': True},
                'small': {'size': (20, 20), 'crop': True},
            },
            'other_app': {
                'sidebar': {'size': (150, 250)},
            }
        }
        self.__aliases = aliases._aliases
        aliases._aliases = {}
        aliases.populate_from_settings()

        if self.create_file:
            self.storage = utils.TemporaryStorage()
            # Save a test image.
            self.create_image(self.storage, 'avatars/test.jpg')
            # Set the test model to use the current temporary storage.
            field = models.Profile._meta.get_field('avatar')
            field.storage = self.storage
            field.thumbnail_storage = self.storage

    def tearDown(self):
        aliases._aliases = self.__aliases
        if self.create_file:
            self.storage.delete_temporary_storage()
        super().tearDown()


class AliasTest(BaseTest):

    def test_global(self):
        self.assertEqual(aliases.get('invalid'), None)
        self.assertEqual(aliases.get('small'), {'size': (100, 100)})
        self.assertEqual(aliases.get('avatar'), None)
        self.assertEqual(aliases.get('banner'), None)

    def test_target(self):
        self.assertEqual(
            aliases.get(
                'avatar', target='easy_thumbnails_tests.Profile.avatar'),
            {'size': (80, 80), 'crop': True})
        self.assertEqual(
            aliases.get(
                'small', target='easy_thumbnails_tests.Profile.avatar'),
            {'size': (20, 20), 'crop': True})

    def test_partial_target(self):
        self.assertEqual(
            aliases.get(
                'banner', target='easy_thumbnails_tests.Profile.avatar'),
            {'size': (600, 80), 'crop': True})
        self.assertEqual(
            aliases.get('banner', target='easy_thumbnails_tests.Profile'),
            {'size': (600, 80), 'crop': True})
        self.assertEqual(
            aliases.get('banner', target='easy_thumbnails_tests'), None)

    def test_target_fallback(self):
        # Unknown target.
        self.assertEqual(
            aliases.get(
                'small', target='easy_thumbnails_tests.Profile.not_avatar'),
            {'size': (100, 100)})
        # Known target with no matching alias (but a matching global alias).
        self.assertEqual(
            aliases.get(
                'medium', target='easy_thumbnails_tests.Profile.avatar'),
            {'size': (300, 300)})
        # Known target with no matching alias.
        self.assertEqual(
            aliases.get(
                'invalid', target='easy_thumbnails_tests.Profile.avatar'),
            None)

    def test_all(self):
        self.assertEqual(
            aliases.all(),
            {
                'large': {'size': (500, 500)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            })

        self.assertEqual(
            aliases.all('unknown_app'),
            {
                'large': {'size': (500, 500)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            })

        self.assertEqual(
            aliases.all('easy_thumbnails_tests.Profile'),
            {
                'banner': {'size': (600, 80), 'crop': True},
                'large': {'size': (200, 200)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            })

        self.assertEqual(
            aliases.all('easy_thumbnails_tests.Profile.avatar'),
            {
                'avatar': {'size': (80, 80), 'crop': True},
                'banner': {'size': (600, 80), 'crop': True},
                'large': {'size': (200, 200)},
                'medium': {'size': (300, 300)},
                'small': {'crop': True, 'size': (20, 20)},
            })

    def test_all_no_global(self):

        self.assertEqual(
            aliases.all(
                'easy_thumbnails_tests.Profile', include_global=False),
                {
                    'banner': {'size': (600, 80), 'crop': True},
                    'large': {'size': (200, 200)},
                })

        self.assertEqual(
            aliases.all(
                'easy_thumbnails_tests.Profile.avatar', include_global=False),
                {
                    'avatar': {'size': (80, 80), 'crop': True},
                    'banner': {'size': (600, 80), 'crop': True},
                    'large': {'size': (200, 200)},
                    'small': {'crop': True, 'size': (20, 20)},
                })

    def test_deferred(self):
        models.Profile.objects.create(avatar='avatars/test.jpg')
        instance = models.Profile.objects.only('avatar').first()
        self.assertEqual(
            aliases.get('small', target=instance.avatar),
            {'size': (20, 20), 'crop': True})


class AliasThumbnailerTest(BaseTest):
    create_file = True

    def test_thumbnailer(self):
        thumbnailer = files.get_thumbnailer(self.storage, 'avatars/test.jpg')
        thumbnailer.thumbnail_storage = self.storage
        thumb = thumbnailer['small']
        self.assertEqual((thumb.width, thumb.height), (100, 75))

    def test_thumbnailer_fieldfile(self):
        profile = models.Profile(avatar='avatars/test.jpg')
        thumbnailer = files.get_thumbnailer(profile.avatar)
        thumb = thumbnailer['small']
        self.assertEqual((thumb.width, thumb.height), (20, 20))


class GenerationBase(BaseTest):
    create_file = True

    def get_signal_handler(self):
        return NotImplementedError("Subclasses should return the handler")

    def setUp(self):
        super().setUp()
        signals.saved_file.connect(
            self.get_signal_handler(), sender=models.Profile)
        # Fix the standard storage to use the test's temporary location.
        self._MEDIA_ROOT = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.storage.temporary_location
        # Make the temporary storage location the default storage for now.
        self._old_default_storage = django_storage.default_storage._wrapped
        django_storage.default_storage._wrapped = self.storage
        self._old_thumbnail_default_storage = storage.thumbnail_default_storage
        storage.thumbnail_default_storage = self.storage

    def tearDown(self):
        # Put the default storage back how we found it.
        storage.thumbnail_default_storage = self._old_thumbnail_default_storage
        django_storage.default_storage._wrapped = self._old_default_storage
        settings.MEDIA_ROOT = self._MEDIA_ROOT
        signals.saved_file.disconnect(
            self.get_signal_handler(), sender=models.Profile)
        super().tearDown()

    def fake_save(self, instance):
        cls = instance.__class__
        pre_save.send(sender=cls, instance=instance)
        for field in cls._meta.fields:
            if isinstance(field, FileField):
                getattr(instance, field.name)._committed = True
        post_save.send(sender=cls, instance=instance)
        return self.storage.listdir('avatars')[1]


class GenerationTest(GenerationBase):
    """
    Test the ``generate_aliases`` signal handler behaviour.
    """

    def get_signal_handler(self):
        return signal_handlers.generate_aliases

    def test_empty(self):
        """
        Thumbnails are not generated if there isn't anything to generate...
        """
        profile = models.Profile(avatar=None)
        files = self.fake_save(profile)
        self.assertEqual(len(files), 1)

    def test_no_change(self):
        """
        Thumbnails are only generated when the file is modified.
        """
        profile = models.Profile(avatar='avatars/test.jpg')
        files = self.fake_save(profile)
        self.assertEqual(len(files), 1)

    def test_changed(self):
        """
        When a file is modified, thumbnails are built for all matching
        non-global aliases.
        """
        profile = models.Profile(avatar='avatars/test.jpg')
        profile.avatar._committed = False
        files = self.fake_save(profile)
        # 1 source, 4 thumbs.
        self.assertEqual(len(files), 5)

    def test_deleted(self):
        profile = models.Profile(avatar='avatars/test.jpg')
        profile.avatar.delete(save=False)
        files = self.fake_save(profile)
        self.assertEqual(len(files), 0)

    def test_clearable(self):
        """
        A ClearablFileInput will set field value to False before pre_save
        """
        profile = models.Profile(avatar='avatars/test.jpg')
        cls = profile.__class__

        profile.avatar = False
        pre_save.send(sender=cls, instance=profile)

        # Saving will then properly clear
        profile.avatar = ''
        post_save.send(sender=cls, instance=profile)

        # FileField is cleared, but not explicitly deleted, file remains
        files = self.storage.listdir('avatars')[1]
        self.assertEqual(len(files), 1)

    def test_standard_filefield(self):
        profile = models.Profile(avatar='avatars/test.jpg')
        # Attach a File object to the FileField descriptor, emulating an
        # upload.
        with self.storage.open(self.create_image(self.storage, 'avatars/second.jpg')) as logo:
            profile.logo = logo
            list_files = self.fake_save(profile)

            # 2 source, 2 thumbs.
            self.assertEqual(len(list_files), 4)


class GlobalGenerationTest(GenerationBase):
    """
    Test the ``generate_aliases_global`` signal handler behaviour.
    """

    def get_signal_handler(self):
        return signal_handlers.generate_aliases_global

    def test_no_change(self):
        """
        Thumbnails are only generated when the file is modified.
        """
        profile = models.Profile(avatar='avatars/test.jpg')
        files = self.fake_save(profile)
        self.assertEqual(len(files), 1)

    def test_changed(self):
        """
        When a file is modified, thumbnails are built for all matching and
        project-wide aliases.
        """
        profile = models.Profile(avatar='avatars/test.jpg')
        profile.avatar._committed = False
        files = self.fake_save(profile)
        # 1 source, 4 specific thumbs, 1 project-wide thumb.
        self.assertEqual(len(files), 6)
