from django.template import Template, Context, TemplateSyntaxError
try:
    from PIL import Image
except ImportError:
    import Image

from django.core.files import storage

from easy_thumbnails import test, alias
from easy_thumbnails.conf import settings
from easy_thumbnails.files import get_thumbnailer


class Base(test.BaseTest):

    def setUp(self):
        super(Base, self).setUp()
        self.storage = test.TemporaryStorage()
        # Save a test image.
        self.filename = self.create_image(self.storage, 'test.jpg')

        # Required so that IOError's get wrapped as TemplateSyntaxError
        settings.TEMPLATE_DEBUG = True

    def tearDown(self):
        self.storage.delete_temporary_storage()
        super(Base, self).tearDown()

    def render_template(self, source):
        source_image = get_thumbnailer(self.storage, self.filename)
        source_image.thumbnail_storage = self.storage
        context = Context({
            'source': source_image,
            'filename': self.filename,
            'invalid_filename': 'not%s' % self.filename,
            'size': (90, 100),
            'invalid_size': (90, 'fish'),
            'strsize': '80x90',
            'invalid_strsize': ('1notasize2'),
            'invalid_q': 'notanumber'})
        source = '{% load thumbnail %}' + source
        return Template(source).render(context)

    def verify_thumbnail(self, expected_size, options, source_filename=None,
                         transparent=False):
        if source_filename is None:
            source_filename = self.filename
        self.assert_(isinstance(options, dict))
        # Verify that the thumbnail file exists
        expected_filename = get_thumbnailer(self.storage, source_filename)\
            .get_thumbnail_name(options, transparent=transparent)

        self.assert_(self.storage.exists(expected_filename),
                     'Thumbnail file %r not found' % expected_filename)

        # Verify the thumbnail has the expected dimensions
        image = Image.open(self.storage.open(expected_filename))
        self.assertEqual(image.size, expected_size)

        return expected_filename


class ThumbnailTagTest(Base):
    restore_settings = ['THUMBNAIL_DEBUG', 'TEMPLATE_DEBUG']

    def testTagInvalid(self):
        # No args, or wrong number of args
        src = '{% thumbnail %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)
        src = '{% thumbnail source %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)
        src = '{% thumbnail source 80x80 as variable crop %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Invalid option
        src = '{% thumbnail source 240x200 invalid %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Old comma separated options format can only have an = for quality
        src = '{% thumbnail source 80x80 crop=1,quality=1 %}'
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Invalid quality
        src_invalid = '{% thumbnail source 240x200 quality=invalid_q %}'
        src_missing = '{% thumbnail source 240x200 quality=missing_q %}'
        # ...with THUMBNAIL_DEBUG = False
        settings.THUMBNAIL_DEBUG = False
        self.assertEqual(self.render_template(src_invalid), '')
        self.assertEqual(self.render_template(src_missing), '')
        # ...and with THUMBNAIL_DEBUG = True
        settings.THUMBNAIL_DEBUG = True
        self.assertRaises(TemplateSyntaxError, self.render_template,
                          src_invalid)
        self.assertRaises(TemplateSyntaxError, self.render_template,
                          src_missing)

        # Invalid source
        src = '{% thumbnail invalid_source 80x80 %}'
        src_on_context = '{% thumbnail invalid_source 80x80 as thumb %}'
        # ...with THUMBNAIL_DEBUG = False
        settings.THUMBNAIL_DEBUG = False
        self.assertEqual(self.render_template(src), '')
        # ...and with THUMBNAIL_DEBUG = True
        settings.THUMBNAIL_DEBUG = True
        self.assertRaises(TemplateSyntaxError, self.render_template, src)
        self.assertRaises(TemplateSyntaxError, self.render_template,
                          src_on_context)

        # Non-existant source
        src = '{% thumbnail non_existant_source 80x80 %}'
        src_on_context = '{% thumbnail non_existant_source 80x80 as thumb %}'
        # ...with THUMBNAIL_DEBUG = False
        settings.THUMBNAIL_DEBUG = False
        self.assertEqual(self.render_template(src), '')
        # ...and with THUMBNAIL_DEBUG = True
        settings.THUMBNAIL_DEBUG = True
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Invalid size as a tuple:
        src = '{% thumbnail source invalid_size %}'
        # ...with THUMBNAIL_DEBUG = False
        settings.THUMBNAIL_DEBUG = False
        self.assertEqual(self.render_template(src), '')
        # ...and THUMBNAIL_DEBUG = True
        settings.THUMBNAIL_DEBUG = True
        self.assertRaises(TemplateSyntaxError, self.render_template, src)
        # Invalid size as a string:
        src = '{% thumbnail source invalid_strsize %}'
        # ...with THUMBNAIL_DEBUG = False
        settings.THUMBNAIL_DEBUG = False
        self.assertEqual(self.render_template(src), '')
        # ...and THUMBNAIL_DEBUG = True
        settings.THUMBNAIL_DEBUG = True
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

        # Non-existant size
        src = '{% thumbnail source non_existant_size %}'
        # ...with THUMBNAIL_DEBUG = False
        settings.THUMBNAIL_DEBUG = False
        self.assertEqual(self.render_template(src), '')
        # ...and THUMBNAIL_DEBUG = True
        settings.THUMBNAIL_DEBUG = True
        self.assertRaises(TemplateSyntaxError, self.render_template, src)

    def testTag(self):
        # Set THUMBNAIL_DEBUG = True to make it easier to trace any failures
        settings.THUMBNAIL_DEBUG = True

        # Basic
        output = self.render_template('src="'
            '{% thumbnail source 240x240 %}"')
        expected = self.verify_thumbnail((240, 180), {'size': (240, 240)})
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.assertEqual(output, 'src="%s"' % expected_url)

        # Size from context variable
        # as a tuple:
        output = self.render_template('src="'
            '{% thumbnail source size %}"')
        expected = self.verify_thumbnail((90, 68), {'size': (90, 100)})
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.assertEqual(output, 'src="%s"' % expected_url)
        # as a string:
        output = self.render_template('src="'
            '{% thumbnail source strsize %}"')
        expected = self.verify_thumbnail((80, 60), {'size': (80, 90)})
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.assertEqual(output, 'src="%s"' % expected_url)

        # On context
        output = self.render_template('height:'
            '{% thumbnail source 240x240 as thumb %}{{ thumb.height }}')
        self.assertEqual(output, 'height:180')

        # With options and quality
        output = self.render_template('src="'
            '{% thumbnail source 240x240 sharpen crop quality=95 %}"')
        # Note that the opts are sorted to ensure a consistent filename.
        expected = self.verify_thumbnail((240, 240), {'size': (240, 240),
            'crop': True, 'sharpen': True, 'quality': 95})
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.assertEqual(output, 'src="%s"' % expected_url)

        # With option and quality on context (also using its unicode method to
        # display the url)
        output = self.render_template(
            '{% thumbnail source 240x240 sharpen crop quality=95 as thumb %}'
            'width:{{ thumb.width }}, url:{{ thumb.url }}')
        self.assertEqual(output, 'width:240, url:%s' % expected_url)

        # One dimensional resize
        output = self.render_template('src="{% thumbnail source 100x0 %}"')
        expected = self.verify_thumbnail((100, 75), {'size': (100, 0)})
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.assertEqual(output, 'src="%s"' % expected_url)


class ThumbnailerBase(Base):
    restore_settings = ['THUMBNAIL_ALIASES', 'THUMBNAIL_MEDIA_ROOT']

    def setUp(self):
        super(ThumbnailerBase, self).setUp()
        settings.THUMBNAIL_MEDIA_ROOT = self.storage.path('')
        settings.THUMBNAIL_ALIASES = {
            '': {
                'small': {'size': (20, 20), 'crop': True},
            },
        }
        alias.aliases.populate_from_settings()
        # Make the temporary storage location the default storage for now.
        self._old_default_storage = storage.default_storage._wrapped
        storage.default_storage._wrapped = self.storage

    def tearDown(self):
        # Put the default storage back how we found it.
        storage.default_storage._wrapped = self._old_default_storage
        super(ThumbnailerBase, self).tearDown()
        # Repopulate the aliases (setting reverted by super)
        alias.aliases.populate_from_settings()


class ThumbnailerFilterTest(ThumbnailerBase):

    def test_get(self):
        src = '{% with t=filename|thumbnailer %}'\
            '{{ t.small.url }}{% endwith %}'
        output = self.render_template(src)
        expected = self.verify_thumbnail((20, 20),
            settings.THUMBNAIL_ALIASES['']['small'])
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.assertEqual(output, expected_url)

    def test_invalid(self):
        src = '{% with t=invalid_filename|thumbnailer %}'\
            '{{ t.small.url }}{% endwith %}'
        output = self.render_template(src)
        self.assertEqual(output, '')


class ThumbnailerPassiveFilterTest(ThumbnailerBase):

    def test_check_generate(self):
        src = '{% with t=filename|thumbnailer_passive %}'\
            '{{ t.generate }}{% endwith %}'
        output = self.render_template(src)
        self.assertEqual(output, 'False')

    def test_get_existing(self):
        options = settings.THUMBNAIL_ALIASES['']['small']
        # Pregenerate the thumbnail.
        get_thumbnailer(self.storage, self.filename).get_thumbnail(options)

        src = '{% with t=filename|thumbnailer_passive %}'\
            '{{ t.small.url }}{% endwith %}'
        output = self.render_template(src)
        expected = self.verify_thumbnail((20, 20), options)
        expected_url = ''.join((settings.MEDIA_URL, expected))
        self.assertEqual(output, expected_url)

    def test_get_missing(self):
        src = '{% with t=filename|thumbnailer_passive %}'\
            '{{ t.small.url }}{% endwith %}'
        output = self.render_template(src)
        self.assertEqual(output, '')

    def test_invalid(self):
        src = '{% with t=invalid_filename|thumbnailer_passive %}'\
            '{{ t.small.url }}{% endwith %}'
        output = self.render_template(src)
        self.assertEqual(output, '')
