from io import BytesIO
from os import path

from django.test import TestCase
from easy_thumbnails import files, utils, signals, exceptions, models, engine
from easy_thumbnails.conf import settings
from easy_thumbnails.options import ThumbnailOptions
from easy_thumbnails.tests import utils as test
from PIL import Image
try:
    from testfixtures import LogCapture
except ImportError:
    LogCapture = None
import unittest


class FilesTest(test.BaseTest):

    def setUp(self):
        super().setUp()
        self.storage = test.TemporaryStorage()
        self.remote_storage = test.FakeRemoteStorage()

        # Save a test image in both storages.
        filename = self.create_image(self.storage, 'test.jpg')
        self.thumbnailer = files.get_thumbnailer(self.storage, filename)
        self.thumbnailer.thumbnail_storage = self.storage

        filename = self.create_image(self.remote_storage, 'test.jpg')
        self.remote_thumbnailer = files.get_thumbnailer(
            self.remote_storage, filename)
        self.remote_thumbnailer.thumbnail_storage = self.remote_storage

        # Create another thumbnailer for extension test.
        self.ext_thumbnailer = files.get_thumbnailer(self.storage, filename)
        self.ext_thumbnailer.thumbnail_storage = self.storage

        # Generate test transparent images.
        filename = self.create_image(
            self.storage, 'transparent.png', image_mode='RGBA',
            image_format='PNG')
        self.transparent_thumbnailer = files.get_thumbnailer(
            self.storage, filename)
        self.transparent_thumbnailer.thumbnail_storage = self.storage

        filename = self.create_image(
            self.storage, 'transparent-greyscale.png', image_mode='LA',
            image_format='PNG')
        self.transparent_greyscale_thumbnailer = files.get_thumbnailer(
            self.storage, filename)
        self.transparent_greyscale_thumbnailer.thumbnail_storage = self.storage

    def tearDown(self):
        self.storage.delete_temporary_storage()
        self.remote_storage.delete_temporary_storage()
        super().tearDown()

    def test_tag(self):
        local = self.thumbnailer.get_thumbnail({'size': (100, 100)})
        remote = self.remote_thumbnailer.get_thumbnail({'size': (100, 100)})

        self.assertEqual(
            local.tag(), '<img alt="" height="75" src="%s" width="100" '
            '/>' % local.url)
        self.assertEqual(
            local.tag(alt='A & B'), '<img alt="A &amp; B" height="75" '
            'src="%s" width="100" />' % local.url)

        # Can turn off dimensions.
        self.assertEqual(
            remote.tag(use_size=False), '<img alt="" src="%s" />' % remote.url)

        # Even a remotely generated thumbnail has the dimensions cached if it
        # was just created.
        self.assertEqual(
            remote.tag(),
            '<img alt="" height="75" src="%s" width="100" />' % remote.url)

        # Future requests to thumbnails on remote storage don't get
        # dimensions...
        remote = self.remote_thumbnailer.get_thumbnail({'size': (100, 100)})
        self.assertEqual(
            remote.tag(), '<img alt="" src="%s" />' % remote.url)
        # ...unless explicitly requested.
        self.assertEqual(
            remote.tag(use_size=True),
            '<img alt="" height="75" src="%s" width="100" />' % remote.url)

        # All other arguments are passed through as attributes.
        self.assertEqual(
            local.tag(**{'rel': 'A&B', 'class': 'fish'}),
            '<img alt="" class="fish" height="75" rel="A&amp;B" '
            'src="%s" width="100" />' % local.url)

    def test_tag_cached_dimensions(self):
        settings.THUMBNAIL_CACHE_DIMENSIONS = True
        self.remote_thumbnailer.get_thumbnail({'size': (100, 100)})

        # Look up thumbnail again to ensure dimensions are a *really* cached.
        remote = self.remote_thumbnailer.get_thumbnail({'size': (100, 100)})
        self.assertEqual(
            remote.tag(),
            '<img alt="" height="75" src="%s" width="100" />' % remote.url)

    def test_transparent_thumbnailing(self):
        thumb_file = self.thumbnailer.get_thumbnail(
            {'size': (100, 100)})
        thumb_file.seek(0)
        with Image.open(thumb_file) as thumb:
            self.assertFalse(
                utils.is_transparent(thumb),
                "%s shouldn't be transparent." % thumb_file.name)

        thumb_file = self.transparent_thumbnailer.get_thumbnail(
            {'size': (100, 100)})
        thumb_file.seek(0)
        with Image.open(thumb_file) as thumb:
            self.assertTrue(
                utils.is_transparent(thumb),
                "%s should be transparent." % thumb_file.name)

        thumb_file = self.transparent_greyscale_thumbnailer.get_thumbnail(
            {'size': (100, 100)})
        thumb_file.seek(0)
        with Image.open(thumb_file) as thumb:
            self.assertTrue(
                utils.is_transparent(thumb),
                "%s should be transparent." % thumb_file.name)

    def test_missing_thumb(self):
        opts = {'size': (100, 100)}
        thumb = self.thumbnailer.get_thumbnail(opts)
        thumb_cache = self.thumbnailer.get_thumbnail_cache(
            thumbnail_name=thumb.name)
        thumb_cache.delete()
        thumb.storage.delete(thumb.name)
        self.thumbnailer.get_thumbnail(opts)

    def test_missing_thumb_from_storage(self):
        opts = {'size': (100, 100)}
        thumb = self.thumbnailer.get_thumbnail(opts)
        thumb.storage.delete(thumb.name)
        new_thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual(thumb.name, new_thumb.name)
        self.assertTrue(thumb.storage.exists(new_thumb.name))

    def test_missing_remote_thumb(self):
        opts = {'size': (100, 100)}
        thumb = self.remote_thumbnailer.get_thumbnail(opts)
        thumb_cache = self.remote_thumbnailer.get_thumbnail_cache(
            thumbnail_name=thumb.name)
        thumb_cache.delete()
        thumb.storage.delete(thumb.name)
        self.remote_thumbnailer.get_thumbnail(opts)

    def test_missing_source(self):
        opts = {'size': (100, 100)}
        self.storage.delete(self.thumbnailer.name)
        self.assertRaises(
            exceptions.InvalidImageFormatError,
            self.thumbnailer.get_thumbnail, opts)

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

    def test_subsampling(self):
        samplings = {
            0: (1, 1, 1, 1, 1, 1),
            1: (2, 1, 1, 1, 1, 1),
            2: (2, 2, 1, 1, 1, 1),
        }
        thumb = self.ext_thumbnailer.get_thumbnail({'size': (100, 100)})
        with Image.open(thumb.path) as im:
            self.assertNotIn('ss', thumb.name)
            sampling = im.layer[0][1:3] + im.layer[1][1:3] + im.layer[2][1:3]
            self.assertEqual(sampling, samplings[2])

        thumb = self.ext_thumbnailer.get_thumbnail(
            {'size': (100, 100), 'subsampling': 1})
        with Image.open(thumb.path) as im:
            self.assertIn('ss1', thumb.name)
            sampling = im.layer[0][1:3] + im.layer[1][1:3] + im.layer[2][1:3]
            self.assertEqual(sampling, samplings[1])

        thumb = self.ext_thumbnailer.get_thumbnail(
            {'size': (100, 100), 'subsampling': 0})
        with Image.open(thumb.path) as im:
            self.assertIn('ss0', thumb.name)
            sampling = im.layer[0][1:3] + im.layer[1][1:3] + im.layer[2][1:3]
            self.assertEqual(sampling, samplings[0])

    def test_default_subsampling(self):
        settings.THUMBNAIL_DEFAULT_OPTIONS = {'subsampling': 1}
        thumb = self.ext_thumbnailer.get_thumbnail({'size': (100, 100)})
        with Image.open(thumb.path) as im:
            self.assertIn('ss1', thumb.name)
            sampling = im.layer[0][1:3] + im.layer[1][1:3] + im.layer[2][1:3]
            self.assertEqual(sampling, (2, 1, 1, 1, 1, 1))

    @unittest.skipIf(
        'easy_thumbnails.optimize' not in settings.INSTALLED_APPS,
        'optimize app not installed')
    @unittest.skipIf(LogCapture is None, 'testfixtures not installed')
    def test_postprocessor(self):
        """use a mock image optimizing post processor doing nothing"""
        settings.THUMBNAIL_OPTIMIZE_COMMAND = {
            'png': 'easy_thumbnails/tests/mockoptim.py {filename}'}
        with LogCapture() as logcap:
            self.ext_thumbnailer.thumbnail_extension = 'png'
            self.ext_thumbnailer.get_thumbnail({'size': (10, 10)})
            actual = tuple(logcap.actual())[0]
            self.assertEqual(actual[0], 'easy_thumbnails.optimize')
            self.assertEqual(actual[1], 'INFO')
            self.assertRegex(
                actual[2],
                '^easy_thumbnails/tests/mockoptim.py [^ ]+ returned nothing$')

    @unittest.skipIf(
        'easy_thumbnails.optimize' not in settings.INSTALLED_APPS,
        'optimize app not installed')
    @unittest.skipIf(LogCapture is None, 'testfixtures not installed')
    def test_postprocessor_fail(self):
        """use a mock image optimizing post processor doing nothing"""
        settings.THUMBNAIL_OPTIMIZE_COMMAND = {
            'png': 'easy_thumbnails/tests/mockoptim_fail.py {filename}'}
        with LogCapture() as logcap:
            self.ext_thumbnailer.thumbnail_extension = 'png'
            self.ext_thumbnailer.get_thumbnail({'size': (10, 10)})
            actual = tuple(logcap.actual())[0]
            self.assertEqual(actual[0], 'easy_thumbnails.optimize')
            self.assertEqual(actual[1], 'ERROR')
            self.assertRegex(
                actual[2], r'^Command\ .+returned non-zero exit status 1.?$')

    def test_USE_TZ(self):
        settings.USE_TZ = True
        self.thumbnailer.get_thumbnail({'size': (10, 20)})

        settings.USE_TZ = False
        self.thumbnailer.get_thumbnail({'size': (20, 40)})

    def test_thumbnailfile_options(self):
        opts = {'size': (50, 50), 'crop': True, 'upscale': True}
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual(thumb.thumbnail_options, ThumbnailOptions(opts))

    def test_get_thumbnail_name(self):
        opts = {
            'size': (50, 50), 'crop': 'smart', 'upscale': True,
            'target': (10, 10)}
        self.assertEqual(
            self.thumbnailer.get_thumbnail_name(opts),
            'test.jpg.50x50_q85_crop-smart_target-10,10_upscale.jpg')

    def test_default_options_setting(self):
        settings.THUMBNAIL_DEFAULT_OPTIONS = {'crop': True}
        opts = {'size': (50, 50)}
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual((thumb.width, thumb.height), (50, 50))

    def test_dimensions_of_cached_image(self):
        opts = {'size': (50, 50)}
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual((thumb.width, thumb.height), (50, 38))
        # Now the thumb has been created, check that retrieving this still
        # gives access to the dimensions.
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual((thumb.width, thumb.height), (50, 38))

    def test_cached_dimensions_of_cached_image(self):
        settings.THUMBNAIL_CACHE_DIMENSIONS = True
        opts = {'size': (50, 50)}
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual((thumb.width, thumb.height), (50, 38))
        # Now the thumb has been created, check that dimesions are in the
        # database.
        dimensions = models.ThumbnailDimensions.objects.all()[0]
        self.assertEqual(
            (thumb.width, thumb.height),
            (dimensions.width, dimensions.height))

    def test_remote_cached_dimensions_queries(self):
        settings.THUMBNAIL_CACHE_DIMENSIONS = True
        opts = {'size': (50, 50)}
        thumb = self.remote_thumbnailer.get_thumbnail(opts)
        thumb.height   # Trigger dimension caching.
        # Get thumb again (which now has cached dimensions).
        thumb = self.remote_thumbnailer.get_thumbnail(opts)
        with self.assertNumQueries(0):
            self.assertEqual(thumb.width, 50)

    def test_add_dimension_cache(self):
        settings.THUMBNAIL_CACHE_DIMENSIONS = True
        opts = {'size': (50, 50)}
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual((thumb.width, thumb.height), (50, 38))
        # Delete the created dimensions.
        models.ThumbnailDimensions.objects.all().delete()
        # Now access the thumbnail again.
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual(models.ThumbnailDimensions.objects.count(), 0)
        thumb.height
        dimensions = models.ThumbnailDimensions.objects.get()
        # and make sure they match when fetched again.
        thumb = self.thumbnailer.get_thumbnail(opts)
        self.assertEqual(
            (thumb.width, thumb.height),
            (dimensions.width, dimensions.height))

        # close the filefield (cause unclosed file ResourceWarning)
        thumb.close()

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
            self.thumbnailer.get_thumbnail(
                {'size': (100, 100)}, generate=False)
            self.assertFalse(hasattr(self.thumbnailer, 'missed_signal'))
            # A thumbnail miss does trigger it.
            options = {'size': (10, 20)}
            thumb = self.thumbnailer.get_thumbnail(options, generate=False)
            self.assertEqual(thumb, None)
            self.assertEqual(
                self.thumbnailer.missed_signal, ThumbnailOptions(options))
        finally:
            signals.thumbnail_created.disconnect(signal_handler)

    def test_progressive_encoding(self):
        thumb = self.thumbnailer.generate_thumbnail(
            {'size': (99, 99), 'crop': True})
        with Image.open(thumb) as thumb_image:
            self.assertFalse(utils.is_progressive(thumb_image))

        thumb = self.thumbnailer.generate_thumbnail(
            {'size': (1, 100), 'crop': True})
        with Image.open(thumb) as thumb_image:
            self.assertTrue(utils.is_progressive(thumb_image))
        thumb = self.thumbnailer.generate_thumbnail(
            {'size': (100, 1), 'crop': True})
        with Image.open(thumb) as thumb_image:
            self.assertTrue(utils.is_progressive(thumb_image))
        thumb = self.thumbnailer.generate_thumbnail({'size': (200, 200)})
        with Image.open(thumb) as thumb_image:
            self.assertTrue(utils.is_progressive(thumb_image))

    def test_no_progressive_encoding(self):
        settings.THUMBNAIL_PROGRESSIVE = False
        thumb = self.thumbnailer.generate_thumbnail({'size': (200, 200)})
        with Image.open(thumb) as thumb_image:
            self.assertFalse(utils.is_progressive(thumb_image))


class FakeSourceGenerator:

    def __init__(self, fail=False):
        self.fail = fail

    def __call__(self, source, **kwargs):
        if self.fail:
            raise ValueError("Fake source generator failed")
        return source


class EngineTest(TestCase):

    def setUp(self):
        self.source = BytesIO(b'file-contents')

    def test_single_fail(self):
        source_generators = [FakeSourceGenerator(fail=True)]
        self.assertRaises(
            ValueError, engine.generate_source_image,
            self.source, {}, source_generators, fail_silently=False)

    def test_single_silent_fail(self):
        source_generators = [FakeSourceGenerator(fail=True)]
        image = engine.generate_source_image(
            self.source, {}, source_generators)
        self.assertEqual(image, None)

    def test_multiple_fail(self):
        source_generators = [
            FakeSourceGenerator(fail=True), FakeSourceGenerator(fail=True)]
        self.assertRaises(
            engine.NoSourceGenerator, engine.generate_source_image,
            self.source, {}, source_generators, fail_silently=False)

    def test_multiple_silent_fail(self):
        source_generators = [
            FakeSourceGenerator(fail=True), FakeSourceGenerator(fail=True)]
        image = engine.generate_source_image(
            self.source, {}, source_generators)
        self.assertEqual(image, None)
