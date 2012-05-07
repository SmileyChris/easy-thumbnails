from django.db import models
from django.core.files.storage import get_storage_class

from easy_thumbnails import files, fields, signals, signal_handlers
from easy_thumbnails.alias import aliases
from easy_thumbnails.conf import settings
from easy_thumbnails.tests import utils


class Profile(models.Model):
    avatar = fields.ThumbnailerField(upload_to='avatars')
    logo = models.FileField(upload_to='avatars')

    class Meta:
        app_label = 'some_app'


class BaseTest(utils.BaseTest):
    create_file = False

    def setUp(self):
        super(BaseTest, self).setUp()
        settings.THUMBNAIL_ALIASES = {
            '': {
                'large': {'size': (500, 500)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            },
            'some_app.Profile': {
                'large': {'size': (200, 200)},
                'banner': {'size': (600, 80), 'crop': True},
            },
            'some_app.Profile.avatar': {
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
            Profile._meta.get_field('avatar').storage = self.storage
            Profile._meta.get_field('avatar').thumbnail_storage = self.storage

    def tearDown(self):
        aliases._aliases = self.__aliases
        if self.create_file:
            self.storage.delete_temporary_storage()
        super(BaseTest, self).tearDown()


class AliasTest(BaseTest):

    def test_global(self):
        self.assertEqual(aliases.get('invalid'), None)
        self.assertEqual(aliases.get('small'), {'size': (100, 100)})
        self.assertEqual(aliases.get('avatar'), None)
        self.assertEqual(aliases.get('banner'), None)

    def test_target(self):
        self.assertEqual(
            aliases.get('avatar', target='some_app.Profile.avatar'),
            {'size': (80, 80), 'crop': True})
        self.assertEqual(
            aliases.get('small', target='some_app.Profile.avatar'),
            {'size': (20, 20), 'crop': True})

    def test_partial_target(self):
        self.assertEqual(
            aliases.get('banner', target='some_app.Profile.avatar'),
            {'size': (600, 80), 'crop': True})
        self.assertEqual(aliases.get('banner', target='some_app.Profile'),
            {'size': (600, 80), 'crop': True})
        self.assertEqual(aliases.get('banner', target='some_app'), None)

    def test_target_fallback(self):
        # Unknown target.
        self.assertEqual(
            aliases.get('small', target='some_app.Profile.not_avatar'),
            {'size': (100, 100)})
        # Known target with no matching alias (but a matching global alias).
        self.assertEqual(
            aliases.get('medium', target='some_app.Profile.avatar'),
            {'size': (300, 300)})
        # Known target with no matching alias.
        self.assertEqual(
            aliases.get('invalid', target='some_app.Profile.avatar'),
            None)

    def test_all(self):
        self.assertEqual(aliases.all(),
            {
                'large': {'size': (500, 500)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            })

        self.assertEqual(aliases.all('unknown_app'),
            {
                'large': {'size': (500, 500)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            })

        self.assertEqual(aliases.all('some_app.Profile'),
            {
                'banner': {'size': (600, 80), 'crop': True},
                'large': {'size': (200, 200)},
                'medium': {'size': (300, 300)},
                'small': {'size': (100, 100)},
            })

        self.assertEqual(aliases.all('some_app.Profile.avatar'),
            {
                'avatar': {'size': (80, 80), 'crop': True},
                'banner': {'size': (600, 80), 'crop': True},
                'large': {'size': (200, 200)},
                'medium': {'size': (300, 300)},
                'small': {'crop': True, 'size': (20, 20)},
            })

    def test_all_no_global(self):

        self.assertEqual(
            aliases.all('some_app.Profile', include_global=False),
            {
                'banner': {'size': (600, 80), 'crop': True},
                'large': {'size': (200, 200)},
            })

        self.assertEqual(
            aliases.all('some_app.Profile.avatar', include_global=False),
            {
                'avatar': {'size': (80, 80), 'crop': True},
                'banner': {'size': (600, 80), 'crop': True},
                'large': {'size': (200, 200)},
                'small': {'crop': True, 'size': (20, 20)},
            })


class AliasThumbnailerTest(BaseTest):
    create_file = True

    def test_thumbnailer(self):
        thumbnailer = files.get_thumbnailer(self.storage, 'avatars/test.jpg')
        thumbnailer.thumbnail_storage = self.storage
        thumb = thumbnailer['small']
        self.assertEqual((thumb.width, thumb.height), (100, 75))

    def test_thumbnailer_fieldfile(self):
        profile = Profile(avatar='avatars/test.jpg')
        thumbnailer = files.get_thumbnailer(profile.avatar)
        thumb = thumbnailer['small']
        self.assertEqual((thumb.width, thumb.height), (20, 20))


class GenerationBase(BaseTest):
    create_file = True

    def get_signal_handler(self):
        return NotImplementedError("Subclasses should return the handler")

    def setUp(self):
        super(GenerationBase, self).setUp()
        signals.saved_file.connect(self.get_signal_handler(), sender=Profile)
        # Fix the standard storage to use the test's temporary location.
        settings.MEDIA_ROOT = self.storage.temporary_location

    def tearDown(self):
        signals.saved_file.disconnect(self.get_signal_handler(),
            sender=Profile)
        super(GenerationBase, self).tearDown()

    def fake_save(self, instance):
        cls = instance.__class__
        models.signals.pre_save.send(sender=cls, instance=instance)
        for field in cls._meta.fields:
            if isinstance(field, models.FileField):
                getattr(instance, field.name)._committed = True
        models.signals.post_save.send(sender=cls, instance=instance)
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
        profile = Profile(avatar=None)
        files = self.fake_save(profile)
        self.assertEqual(len(files), 1)

    def test_no_change(self):
        """
        Thumbnails are only generated when the file is modified.
        """
        profile = Profile(avatar='avatars/test.jpg')
        files = self.fake_save(profile)
        self.assertEqual(len(files), 1)

    def test_changed(self):
        """
        When a file is modified, thumbnails are built for all matching
        non-global aliases.
        """
        profile = Profile(avatar='avatars/test.jpg')
        profile.avatar._committed = False
        files = self.fake_save(profile)
        # 1 source, 4 thumbs.
        self.assertEqual(len(files), 5)

    def test_deleted(self):
        profile = Profile(avatar='avatars/test.jpg')
        profile.avatar.delete(save=False)
        files = self.fake_save(profile)
        self.assertEqual(len(files), 0)

    def test_standard_filefield(self):
        profile = Profile(avatar='avatars/test.jpg')
        # Attach a File object to the FileField descriptor, emulating an
        # upload.
        profile.logo = self.storage.open(
            self.create_image(self.storage, 'avatars/second.jpg'))
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
        profile = Profile(avatar='avatars/test.jpg')
        files = self.fake_save(profile)
        self.assertEqual(len(files), 1)

    def test_changed(self):
        """
        When a file is modified, thumbnails are built for all matching and
        project-wide aliases.
        """
        profile = Profile(avatar='avatars/test.jpg')
        profile.avatar._committed = False
        files = self.fake_save(profile)
        # 1 source, 4 specific thumbs, 1 project-wide thumb.
        self.assertEqual(len(files), 6)
