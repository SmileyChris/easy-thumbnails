from easy_thumbnails import files
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

    def tearDown(self):
        self.storage.delete_temporary_storage()
        self.remote_storage.delete_temporary_storage()
        super(FilesTest, self).tearDown()

    def test_tag(self):
        local = self.thumbnailer.get_thumbnail({'size': (100, 100)})
        remote = self.remote_thumbnailer.get_thumbnail({'size': (100, 100)})

        self.assertEqual(local.tag(), '<img alt="" height="75" src="test.jpg'
            '.100x100_q85.jpg" width="100" />')
        self.assertEqual(local.tag(alt='A & B'), '<img alt="A &amp; B" '
            'height="75" src="test.jpg.100x100_q85.jpg" width="100" />')

        # Can turn off dimensions.
        self.assertEqual(remote.tag(use_size=False), '<img alt="" '
            'src="test.jpg.100x100_q85.jpg" />')

        # Thumbnails on remote storage don't get dimensions...  
        self.assertEqual(remote.tag(), '<img alt="" '
            'src="test.jpg.100x100_q85.jpg" />')
        # ...unless explicitly requested.
        self.assertEqual(remote.tag(use_size=True), '<img alt="" height="75" '
            'src="test.jpg.100x100_q85.jpg" width="100" />')

        # All other arguments are passed through as attributes.
        self.assertEqual(local.tag(**{'rel': 'A&B', 'class': 'fish'}),
            '<img alt="" class="fish" height="75" rel="A&amp;B" '
            'src="test.jpg.100x100_q85.jpg" width="100" />')
