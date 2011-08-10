from easy_thumbnails import files, utils
from easy_thumbnails.tests import utils as test_utils
from django.core.files.base import ContentFile
from StringIO import StringIO
try:
    from PIL import Image
except ImportError:
    import Image


class FilesTest(test_utils.BaseTest):
    
    def setUp(self):
        super(FilesTest, self).setUp()
        self.storage = test_utils.TemporaryStorage()
        self.remote_storage = test_utils.FakeRemoteStorage()

        # Generate a test image.
        data = StringIO()
        Image.new('RGB', (800, 600)).save(data, 'JPEG')
        data.seek(0)
        image_file = ContentFile(data.read())

        # Save the test image in both storages.
        filename = self.storage.save('test.jpg', image_file)
        self.thumbnailer = files.get_thumbnailer(self.storage, filename)
        self.thumbnailer.thumbnail_storage = self.storage
        
        filename = self.remote_storage.save('test.jpg', image_file)
        self.remote_thumbnailer = files.get_thumbnailer(self.remote_storage,
            filename)
        self.remote_thumbnailer.thumbnail_storage = self.remote_storage

        # Generate test transparent images.
        data = StringIO()
        Image.new('RGBA', (800, 600)).save(data, 'PNG')
        data.seek(0)
        image_file = ContentFile(data.read())
        filename = self.storage.save('transparent.png', image_file)
        self.transparent_thumbnailer = files.get_thumbnailer(self.storage,
            filename)
        self.transparent_thumbnailer.thumbnail_storage = self.storage

        data = StringIO()
        Image.new('LA', (800, 600)).save(data, 'PNG')
        data.seek(0)
        image_file = ContentFile(data.read())
        filename = self.storage.save('transparent-greyscale.png', image_file)
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
