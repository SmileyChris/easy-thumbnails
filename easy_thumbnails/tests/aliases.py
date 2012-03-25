from django.conf import settings
from django.db import models

from easy_thumbnails import files, fields
from easy_thumbnails.alias import aliases
from easy_thumbnails.tests import utils


class Profile(models.Model):
    avatar = fields.ThumbnailerField(upload_to='avatars')

    class Meta:
        app_label = 'some_app'


class BaseTest(utils.BaseTest):

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
        }
        self.__aliases = aliases._aliases
        aliases._aliases = {}
        aliases.populate_from_settings()

    def tearDown(self):
        aliases._aliases = self.__aliases
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

    def setUp(self):
        super(AliasThumbnailerTest, self).setUp()
        self.storage = utils.TemporaryStorage()
        # Save a test image.
        self.create_image(self.storage, 'avatars/test.jpg')
        # Set the test model to use the current temporary storage.
        Profile._meta.get_field('avatar').storage = self.storage
        Profile._meta.get_field('avatar').thumbnail_storage = self.storage

    def tearDown(self):
        self.storage.delete_temporary_storage()
        super(AliasThumbnailerTest, self).tearDown()

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
