from os import path

from easy_thumbnails import files, utils, signals, test
from easy_thumbnails.conf import settings
try:
    from PIL import Image
except ImportError:
    import Image


class FilesTest(test.BaseTest):

    def setUp(self):
        super(FilesTest, self).setUp()
        self.storage = test.TemporaryStorage()
        self.remote_storage = test.FakeRemoteStorage()

        # Save a test image in both storages.
        filename = self.create_image(self.storage, 'test.jpg')
        self.thumbnailer = files.get_thumbnailer(self.storage, filename)
        self.thumbnailer.thumbnail_storage = self.storage

        filename = self.create_image(self.remote_storage, 'test.jpg')
        self.remote_thumbnailer = files.get_thumbnailer(self.remote_storage,
            filename)
        self.remote_thumbnailer.thumbnail_storage = self.remote_storage

        # Create another thumbnailer for extension test.
        self.ext_thumbnailer = files.get_thumbnailer(self.storage, filename)
        self.ext_thumbnailer.thumbnail_storage = self.storage

        # Generate test transparent images.
        filename = self.create_image(self.storage, 'transparent.png',
            image_mode='RGBA', image_format='PNG')
        self.transparent_thumbnailer = files.get_thumbnailer(self.storage,
            filename)
        self.transparent_thumbnailer.thumbnail_storage = self.storage

        filename = self.create_image(self.storage, 'transparent-greyscale.png',
            image_mode='LA', image_format='PNG')
        self.transparent_greyscale_thumbnailer = files.get_thumbnailer(
            self.storage, filename)
        self.transparent_greyscale_thumbnailer.thumbnail_storage = self.storage

    def tearDown(self):
        self.storage.delete_temporary_storage()
        self.remote_storage.delete_temporary_storage()
        super(FilesTest, self).tearDown()

    def test_tag(self):
        local = self.thumbnailer.get_thumbnail({'size': (100, 100)})
        remote = self.remote_thumbnailer.get_thumbnail({'size': (100, 100)})

        self.assertEqual(local.tag(), '<img alt="" height="75" '
            'src="%s" width="100" />' % local.url)
        self.assertEqual(local.tag(alt='A & B'), '<img alt="A &amp; B" '
            'height="75" src="%s" width="100" />' % local.url)

        # Can turn off dimensions.
        self.assertEqual(remote.tag(use_size=False), '<img alt="" '
            'src="%s" />' % remote.url)

        # Thumbnails on remote storage don't get dimensions...
        self.assertEqual(remote.tag(), '<img alt="" '
            'src="%s" />' % remote.url)
        # ...unless explicitly requested.
        self.assertEqual(remote.tag(use_size=True), '<img alt="" height="75" '
            'src="%s" width="100" />' % remote.url)

        # All other arguments are passed through as attributes.
        self.assertEqual(local.tag(**{'rel': 'A&B', 'class': 'fish'}),
            '<img alt="" class="fish" height="75" rel="A&amp;B" '
            'src="%s" width="100" />' % local.url)

    def test_transparent_thumbnailing(self):
        thumb_file = self.thumbnailer.get_thumbnail(
            {'size': (100, 100)})
        thumb_file.seek(0)
        thumb = Image.open(thumb_file)
        self.assertFalse(utils.is_transparent(thumb),
            "%s shouldn't be transparent." % thumb_file.name)

        thumb_file = self.transparent_thumbnailer.get_thumbnail(
            {'size': (100, 100)})
        thumb_file.seek(0)
        thumb = Image.open(thumb_file)
        self.assertTrue(utils.is_transparent(thumb),
            "%s should be transparent." % thumb_file.name)

        thumb_file = self.transparent_greyscale_thumbnailer.get_thumbnail(
            {'size': (100, 100)})
        thumb_file.seek(0)
        thumb = Image.open(thumb_file)
        self.assertTrue(utils.is_transparent(thumb),
            "%s should be transparent." % thumb_file.name)

    def test_extensions(self):
        self.ext_thumbnailer.thumbnail_extension = 'png'
        thumb = self.ext_thumbnailer.get_thumbnail({'size': (100, 100)})
        self.assertEqual(path.splitext(thumb.name)[1], '.png')

        self.ext_thumbnailer.thumbnail_preserve_extensions = ('foo',)
        thumb = self.ext_thumbnailer.get_thumbnail({'size': (100, 100)})
        self.assertEqual(path.splitext(thumb.name)[1], '.png')

        self.ext_thumbnailer.thumbnail_preserve_extensions = True
        thumb = self.ext_thumbnailer.get_thumbnail({'size': (100, 100)})
        self.assertEqual(path.splitext(thumb.name)[1], '.jpg')

        self.ext_thumbnailer.thumbnail_preserve_extensions = ('foo', 'jpg')
        thumb = self.ext_thumbnailer.get_thumbnail({'size': (100, 100)})
        self.assertEqual(path.splitext(thumb.name)[1], '.jpg')

    def test_USE_TZ(self):
        settings.USE_TZ = True
        self.thumbnailer.get_thumbnail({'size': (10, 20)})

        settings.USE_TZ = False
        self.thumbnailer.get_thumbnail({'size': (20, 40)})

    def test_thumbnailfile_options(self):
        opts = {'size': (50, 50), 'crop': True, 'upscale': True}
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual(thumb.thumbnail_options, opts)

    def test_default_options_setting(self):
        settings.THUMBNAIL_DEFAULT_OPTIONS = {'crop': True}
        opts = {'size': (50, 50)}
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual((thumb.width, thumb.height), (50, 50))

    def test_thumbnail_created_signal(self):

        def signal_handler(sender, **kwargs):
            sender.signal_received = True

        signals.thumbnail_created.connect(signal_handler)
        try:
            thumb = self.thumbnailer.get_thumbnail({'size': (10, 20)})
            self.assertTrue(hasattr(thumb, 'signal_received'))
        finally:
            signals.thumbnail_created.disconnect(signal_handler)

    def test_passive_thumbnailer(self):
        options = {'size': (10, 10)}

        # Explicitly using the generate=False option on get_thumbnail won't
        # generate a missing thumb.
        thumb = self.thumbnailer.get_thumbnail(options, generate=False)
        self.assertEqual(thumb, None)

        # If the thumbnailer has generate=False, get_thumbnail won't generate a
        # missing thumb by default.
        self.thumbnailer.generate = False
        thumb = self.thumbnailer.get_thumbnail(options)
        self.assertEqual(thumb, None)

        # If the thumbnailer has generate=False, get_thumbnail with
        # generate=True will stiff force generation a missing thumb.
        thumb = self.thumbnailer.get_thumbnail(options, generate=True)
        self.assertTrue(thumb)

        # If the thumbnailer has generate=False, get_thumbnail will still
        # return existing thumbnails.
        thumb = self.thumbnailer.get_thumbnail(options)
        self.assertTrue(thumb)

        # Explicitly using the generate=False option on get_thumbnail will
        # still return existing thumbnails.
        thumb = self.thumbnailer.get_thumbnail(options, generate=False)
        self.assertTrue(thumb)

    def test_thumbnail_missed_signal(self):

        def signal_handler(sender, **kwargs):
            sender.missed_signal = kwargs.get('options')

        signals.thumbnail_missed.connect(signal_handler)
        try:
            # Standard generation doesn't trigger signal.
            self.thumbnailer.get_thumbnail({'size': (100, 100)})
            self.assertFalse(hasattr(self.thumbnailer, 'missed_signal'))
            # Retrieval doesn't trigger signal.
            self.thumbnailer.get_thumbnail({'size': (100, 100)},
                generate=False)
            self.assertFalse(hasattr(self.thumbnailer, 'missed_signal'))
            # A thumbnail miss does trigger it.
            options = {'size': (10, 20)}
            thumb = self.thumbnailer.get_thumbnail(options, generate=False)
            self.assertEqual(thumb, None)
            self.assertEqual(self.thumbnailer.missed_signal, options)
        finally:
            signals.thumbnail_created.disconnect(signal_handler)
