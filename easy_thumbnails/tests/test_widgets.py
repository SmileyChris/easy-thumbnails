from unittest.case import skipIf

from django import VERSION as DJANGO_VERSION
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.widgets import ClearableFileInput

from easy_thumbnails import widgets
from easy_thumbnails.tests import utils as test


class ImageClearableFileInput(test.BaseTest):

    def setUp(self):
        super(ImageClearableFileInput, self).setUp()
        self.storage = test.TemporaryStorage()

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
        self.assertEqual(
            widget.thumbnail_options, {'size': (300, 100), 'crop': True})

    def test_render(self):
        """
        The output contains a link to both the source image and the thumbnail.
        """
        source_filename = self.create_image(self.storage, 'test.jpg')
        widget = widgets.ImageClearableFileInput()

        with self.storage.open(source_filename) as source_file:
            source_file.storage = self.storage
            source_file.thumbnail_storage = self.storage
            html = widget.render('photo', source_file)

        self.assertIn(source_filename, html)
        self.assertIn('.80x80_', html)

    def test_render_custom_thumb_options(self):
        """
        The thumbnail is generated using the options provided to the widget.
        """
        source_filename = self.create_image(self.storage, 'test.jpg')
        options = {'size': (100, 500), 'quality': 90, 'crop': True}
        widget = widgets.ImageClearableFileInput(thumbnail_options=options)

        with self.storage.open(source_filename) as source_file:
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
        widget.template_with_thumbnail = (
            u'%(template)s<br />'
            u'<a href="%(source_url)s">%(thumb)s</a> FOO'
        )

        with self.storage.open(source_filename) as source_file:
            source_file.storage = self.storage
            source_file.thumbnail_storage = self.storage
            html = widget.render('photo', source_file)

        self.assertIn(source_filename, html)
        self.assertIn('.80x80_', html)
        self.assertIn('FOO', html)

    @skipIf(DJANGO_VERSION < (1, 11), 'Custom widget renderer works for Django >=1.11')
    def test_custom_renderer(self):
        """
        The form renderer used to render the thumbnail and the standard
        ``ClearableFileInput`` output can be customized since Django 1.11
        """
        from django.forms.renderers import DjangoTemplates

        source_filename = self.create_image(self.storage, 'test.jpg')
        widget = widgets.ImageClearableFileInput()
        class CustomRenderer(DjangoTemplates):
            def render(self, template_name, context, request=None):
                output = super(DjangoTemplates, self).render(template_name, context, request)
                return output + ' FOOBAR'

        with self.storage.open(source_filename) as source_file:
            source_file.storage = self.storage
            source_file.thumbnail_storage = self.storage
            html = widget.render('photo', source_file, renderer=CustomRenderer())

        self.assertIn(source_filename, html)
        self.assertIn('.80x80_', html)
        self.assertIn('FOOBAR', html)

    def test_render_without_value(self):
        """
        If value not passed, use super widget.
        """
        widget = widgets.ImageClearableFileInput()
        base_widget = ClearableFileInput()
        html = widget.render('photo', None)
        base_html = base_widget.render('photo', None)
        self.assertEqual(base_html, html)

    def test_render_uploaded(self):
        """
        The widget treats UploadedFile as no input.

        Rationale:
        When widget is used in ModelForm and the form (submitted with upload)
        is not valid, widget should discard the value (just like standard
        Django ClearableFileInput does).
        """
        widget = widgets.ImageClearableFileInput()
        base_widget = ClearableFileInput()
        file_name = 'test.jpg'
        # storage=None to get raw content.
        image = self.create_image(None, file_name)
        upload_file = SimpleUploadedFile(file_name, image.getvalue())
        html = widget.render('photo', upload_file)
        base_html = base_widget.render('photo', upload_file)
        self.assertEqual(base_html, html)
        self.assertNotIn(file_name, html)   # Widget is empty.

