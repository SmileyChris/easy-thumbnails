from easy_thumbnails import widgets
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.tests import utils as test_utils
from django.forms.widgets import ClearableFileInput


class ImageClearableFileInput(test_utils.BaseTest):

    def setUp(self):
        super(ImageClearableFileInput, self).setUp()
        self.storage = test_utils.TemporaryStorage()

    def tearDown(self):
        self.storage.delete_temporary_storage()
        super(ImageClearableFileInput, self).tearDown()

    def test_options_default(self):
        """
        If thumbnail options are not passed, default options will be used.
        """
        widget = widgets.ImageClearableFileInput()
        self.assertEqual(widget.thumbnail_options, {'size': (80, 80)})

    def test_options_custom(self):
        """
        A dictionary can be passed as the thumbnail options. The dictionary is
        copied so it isn't just a mutable reference of the original.
        """
        options = {'size': (300, 100), 'crop': True}
        widget = widgets.ImageClearableFileInput(thumbnail_options=options)
        # Changing the options won't change the thumbnail options in the widget
        # now.
        options['crop'] = False
        self.assertEqual(widget.thumbnail_options,
            {'size': (300, 100), 'crop': True})

    def test_render(self):
        """
        The output contains a link to both the source image and the thumbnail.
        """
        source_filename = self.create_image(self.storage, 'test.jpg')
        widget = widgets.ImageClearableFileInput()
        source_file = self.storage.open(source_filename)
        source_file.storage = self.storage
        source_file.thumbnail_storage = self.storage
        html = widget.render('photo', source_file)
        self.assertIn(source_filename, html)
        self.assertIn('.80x80_', html)

    def test_render_custom(self):
        """
        The thumbnail is generated using the options provided to the widget.
        """
        source_filename = self.create_image(self.storage, 'test.jpg')
        options = {'size': (100, 500), 'quality': 90, 'crop': True}
        widget = widgets.ImageClearableFileInput(thumbnail_options=options)
        source_file = self.storage.open(source_filename)
        source_file.storage = self.storage
        source_file.thumbnail_storage = self.storage
        html = widget.render('photo', source_file)
        self.assertIn(source_filename, html)
        self.assertIn('.100x500_q90_crop.jpg', html)

    def test_custom_template(self):
        """
        The template used to render the thumbnail and the standard
        ``ClearableFileInput`` output can be customized.
        """
        source_filename = self.create_image(self.storage, 'test.jpg')
        widget = widgets.ImageClearableFileInput()
        widget.template_with_thumbnail = u'%(template)s<br />'\
            u'<a href="%(source_url)s">%(thumb)s</a> FOO'
        source_file = self.storage.open(source_filename)
        source_file.storage = self.storage
        source_file.thumbnail_storage = self.storage
        html = widget.render('photo', source_file)
        self.assertIn(source_filename, html)
        self.assertIn('.80x80_', html)
        self.assertIn('FOO', html)

    def test_render_without_value(self):
        """
        If value not passed, use super widget.
        """
        widget = widgets.ImageClearableFileInput()
        base_widget = ClearableFileInput()
        html = widget.render('photo', None)
        base_html = base_widget.render('photo', None)
        self.assertEqual(base_html, html)
